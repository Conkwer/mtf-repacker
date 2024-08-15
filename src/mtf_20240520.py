import os
import sys
import struct
import pathlib
import shutil

# Simple check to see if we are running on Windows
def is_windows():
    return os.name == "nt"

# Allowed subcommands
COMMANDS = ["create", "extract", "list"]

def main():
    log_file = None
    if '-l' in sys.argv:
        log_index = sys.argv.index('-l') + 1
        if log_index < len(sys.argv):
            log_file = sys.argv[log_index]
        else:
            print("Error: No log file specified.")
            sys.exit(1)

    if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
        # User has dragged an MTF file to the script
        command = "extract"
        archive = sys.argv[1]
        directory = str(pathlib.Path().resolve())
    elif len(sys.argv) < 5 or sys.argv[1] not in COMMANDS:
        # Display the usage instructions and keep the window open
        print(f"Usage: mtf ({' | '.join(COMMANDS)}) -i input.MTF -o [output_dir]")
        if is_windows():
            # Pause the script on Windows to keep the window open
            input("Press Enter to exit...")
        else:
            # On non-Windows systems, use `os.system('read -p "Press Enter to exit..." -n1 -s; echo ""')` to keep the window open
            os.system('read -p "Press Enter to exit..." -n1 -s; echo ""')
        sys.exit(1)
    else:
        command = sys.argv[1]
        archive = sys.argv[3]
        directory = sys.argv[5] if len(sys.argv) > 5 else ""

    if command == "create":
        dirs = [pathlib.Path(p).resolve() for p in sys.argv[4:]]
        create_archive(archive, dirs)
    elif command == "extract":
        extract_archive(pathlib.Path(directory), pathlib.Path(archive))
    elif command == "list":
        list_archive(pathlib.Path(directory), pathlib.Path(archive), display_only=True, log_file=log_file)

def create_archive(archive, dirs):
    data_offset = 0
    data_size = 0
    header_size = 4
    entries = []

    for dir_info in dirs:
        for path in dir_info.rglob("*"):
            if path.is_file():
                rel_path = str(path.relative_to(dir_info))
                if not is_windows():
                    rel_path = rel_path.replace("\\", "/")
                header_size += len(rel_path) + 1 + 4  # filename, terminating 0, filename length
                header_size += 8  # offset and size
                offset = data_offset
                data_offset += path.stat().st_size
                data_size += path.stat().st_size
                entries.append({
                    "path": str(path),
                    "rel_path": rel_path,
                    "offset": offset,
                    "size": path.stat().st_size,
                })

    # Write the archive
    buf = bytearray(header_size + data_size)
    struct.pack_into("<I", buf, 0, len(entries))
    offset = 4

    for entry in entries:
        # Write name to archive index
        struct.pack_into("<I", buf, offset, len(entry["rel_path"]) + 1)
        offset += 4
        buf[offset : offset + len(entry["rel_path"])] = entry["rel_path"].encode('cp1252')
        buf[offset + len(entry["rel_path"])] = 0
        offset += len(entry["rel_path"]) + 1

        # Write file offset and size
        struct.pack_into("<II", buf, offset, header_size + entry["offset"], entry["size"])
        offset += 8

        print(entry["rel_path"], entry["size"])

    for entry in entries:
        with open(entry["path"], "rb") as f:
            buf[header_size + entry["offset"] : header_size + entry["offset"] + entry["size"]] = f.read()

    with open(archive, "wb") as f:
        f.write(buf)

def extract_archive(directory, archive, display_only=False):
    with open(archive, "rb") as f:
        buf = f.read()

    dv = memoryview(buf)
    count = struct.unpack_from("<I", dv, 0)[0]
    offset = 4

    for _ in range(count):
        name_len = struct.unpack_from("<I", dv, offset)[0]
        offset += 4
        name = dv[offset : offset + name_len - 1].tobytes().decode('cp1252')
        offset += name_len

        file_offset = struct.unpack_from("<I", dv, offset)[0]
        file_size = struct.unpack_from("<I", dv, offset + 4)[0]
        offset += 8

        if not is_windows():
            name = name.replace("\\", "/")

        if not display_only:
            if struct.unpack_from("<I", dv, file_offset)[0] == 0x0BADBEAF:
                # Compressed file, decompress it
                file_data = decompress(dv, file_offset, file_size)
            else:
                file_data = dv[file_offset : file_offset + file_size].tobytes()

            final_path = pathlib.Path(directory, name)
            final_path.parent.mkdir(parents=True, exist_ok=True)
            with open(final_path, "wb") as f:
                f.write(file_data)

        print(name, file_size)

def decompress(dv, offset, size):
    #let compressedSig = dv.getUint32(off + 0, true);
    compressed_size = struct.unpack_from("<I", dv, offset + 4)[0]
    decompressed_size = struct.unpack_from("<I", dv, offset + 8)[0]
    offset += 12

    out = bytearray(size)
    out_idx = 0

    bytes_left = decompressed_size
    while bytes_left > 0:
        chunk_bits = struct.unpack_from("<B", dv, offset)[0]
        offset += 1
        for b in range(8):
            flag = chunk_bits & (1 << b)
            if flag:
                # Copy single byte
                byte = struct.unpack_from("<B", dv, offset)[0]
                offset += 1
                out[out_idx] = byte
                out_idx += 1
                bytes_left -= 1
            else:
                word = struct.unpack_from("<H", dv, offset)[0]
                offset += 2
                if word == 0:
                    break

                count = (word >> 10) + 3
                offset_val = (word & 0x03FF)
                # Copy count+3 bytes starting at offset to the end of the decompression buffer,
                # as explained here: http://wiki.xentax.com/index.php?title=Darkstone
                for _ in range(count):
                    out[out_idx] = out[out_idx - offset_val]
                    out_idx += 1
                    bytes_left -= 1

                if bytes_left < 0:
                    print("Compressed/decompressed size mismatch!", compressed_size, size, decompressed_size)
                    return None

    return out

def list_archive(directory, archive, display_only=False, log_file=None):
    with open(archive, "rb") as f:
        buf = f.read()

    dv = memoryview(buf)
    count = struct.unpack_from("<I", dv, 0)[0]
    offset = 4

    # Delete the existing log file if it exists
    if log_file and os.path.exists(log_file):
        os.remove(log_file)

    for _ in range(count):
        name_len = struct.unpack_from("<I", dv, offset)[0]
        offset += 4
        name = dv[offset : offset + name_len - 1].tobytes().decode('cp1252')
        offset += name_len

        file_offset = struct.unpack_from("<I", dv, offset)[0]
        file_size = struct.unpack_from("<I", dv, offset + 4)[0]
        offset += 8

        if not is_windows():
            name = name.replace("\\", "/")

        if log_file:
            with open(log_file, 'a', encoding='utf-8') as f:  # 'a' for append mode
                f.write(f"{name}, {file_size}\n")
        else:
            print(name, file_size)

if __name__ == "__main__":
    main()