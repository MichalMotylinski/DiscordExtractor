from gzip import decompress
import hashlib
from os.path import join, exists
from re import findall
from datetime import datetime, timedelta
from urllib.parse import urlparse
from os.path import splitext, basename


def read_extensions():
    # Dictionary of supported extensions
    extensions = {"audio/3gpp": ".3gp", "audio/basic": ".au", "audio/mpeg": ".mp3", "audio/xaiff": ".aiff",
                  "audio/x-wav": ".wav", "audio/webm": ".webm", "application/eps": ".eps",
                  "application/font-woff": ".woff", "application/javascript": ".js", "application/json": ".json",
                  "application/msword": ".doc", "application/octet-stream": ".bin", "application/oda": ".oda",
                  "application/opensearchdescription+xml": ".osdx", "application/pdf": ".pdf",
                  "application/postscript": ".ps", "application/vnd.apple.mpegurl": ".m3u",
                  "application/vnd.ms-access": ".mdb", "application/vnd.ms-excel": ".xls",
                  "application/vnd.ms-excel.addin.macroEnabled.12": ".xlam",
                  "application/vnd.ms-excel.sheet.binary.macroEnabled.12": ".xlsb",
                  "application/vnd.ms-excel.sheet.macroEnabled.12": ".xlsm",
                  "application/vnd.ms-excel.template.macroEnabled.12": ".xltm", "application/vnd.ms-powerpoint": ".ppt",
                  "application/vnd.ms-powerpoint.addin.macroEnabled.12": ".ppam",
                  "application/vnd.ms-powerpoint.presentation.macroEnabled.12": ".pptm",
                  "application/vnd.ms-powerpoint.slideshow.macroEnabled.12": ".ppsm",
                  "application/vnd.ms-powerpoint.template.macroEnabled.12": ".potm",
                  "application/vnd.ms-word.document.macroEnabled.12": ".docm",
                  "application/vnd.ms-word.template.macroEnabled.12": ".dotm",
                  "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
                  "application/vnd.openxmlformats-officedocument.presentationml.template": ".potx",
                  "application/vnd.openxmlformats-officedocument.presentationml.slideshow": ".ppsx",
                  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
                  "application/vnd.openxmlformats-officedocument.wordprocessingml.template": ".dotx",
                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
                  "application/vnd.openxmlformats-officedocument.spreadsheetml.template": ".xltx",
                  "application/x-bcpio": ".bcpio", "application/x-cpio": ".cpio", "application/x-csh": ".csh",
                  "application/x-dvi": ".dvi", "application/x-eps": ".eps", "application/x-gtar": ".gtar",
                  "application/x-hdf": ".hdf", "application/x-latex": ".latex", "application/x-mif": ".mif",
                  "application/x-msdos-program": ".exe", "application/x-netcdf": ".cdf",
                  "application/x-python-code": ".pyc", "application/x-tar": ".tar", "application/x-troff-man": ".man",
                  "application/x-troff-me": ".me", "application/x-troff-ms": ".ms", "application/x-troff": ".roff",
                  "application/zipmap": ".zip", "font/woff": ".woff", "font/woff2": ".woff2", "image/eps": ".eps",
                  "image/gif": ".gif", "image/ief": ".ief", "image/jpeg": ".jpg", "image/png": ".png",
                  "image/svg+xml": ".svg", "image/tiff": ".tiff", "image/vnd.microsoft.icon": ".ico",
                  "image/x-eps": ".eps", "image/x-icon": ".ico", "image/x-ms-bmp": ".bmp",
                  "image/x-portable-anymap": ".pnm", "image/x-portable-bitmap": ".pbm",
                  "image/x-portable-greymap": ".pgm", "image/x-portable-pixmap": ".ppm",
                  "image/x-shockwave-flash": ".swf", "image/webp": ".webp", "message/rfc822": ".eml",
                  "text/css": ".css", "text/csv": ".csv", "text/html": ".html", "text/plain": ".txt",
                  "text/richtext": ".rtx", "text/tab-separated-values": ".tsv", "text/xml": ".xml",
                  "text/x-python": ".py", "text/x-setext": ".etx", "text/x-vcard": ".vcf", "text/javascript": ".js",
                  "video/3gpp": ".3gp", "video/mp4": ".mp4", "video/mpeg": ".mpeg", "video/quicktime": ".mov",
                  "video/x-msvideo": ".avi", "video/x-dgi-movie": ".movie", "video/webm": ".webm"}
    return extensions


def hex_time_convert(time_in_microseconds):
    epoch = datetime(1601, 1, 1)
    dirty_time = epoch + timedelta(microseconds=time_in_microseconds)
    date, hmr = str(dirty_time).split(" ", 1)
    date = datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
    hmr = hmr.split(".", 1)[0]
    clean_time = date + " " + hmr
    return clean_time


def get_filename(content_type, resource_content_size, url_data):
    filename = ""
    file_extension = ""
    if not resource_content_size == 0:
        # Pattern matching for chat log file
        if r"/messages?" in url_data.lower():
            try:
                filename = findall(r"(?<=/)([0-9]+)(?=/)", url_data)[0]
            except IndexError:
                # All other files have their names pulled automatically by below functions
                dis = urlparse(url_data)
                filename, ext = splitext(basename(dis.path))
        else:
            dis = urlparse(url_data)
            filename, ext = splitext(basename(dis.path))
        # If filename is too long cut it in size to a max of 60 characters
        if len(filename) > 60:
            filename = filename[0:60]
        # Get extension by comparing content_type to items in custom made list of extensions
        extensions_list = read_extensions()
        if content_type in extensions_list:
            file_extension = extensions_list[content_type]
    return filename, file_extension


def read_http_response(http_response_data):
    server_response = ""
    content_type = ""
    etag = ""
    response_time = ""
    last_modified = ""
    max_age = ""
    server_name = ""
    expire_time = ""
    content_encoding = ""
    server_ip = ""
    timezone = ""

    if http_response_data:
        try:
            string_start = http_response_data.lower().find("http")
            if not string_start == -1:
                string_end = http_response_data.find("\\x00", string_start)
                server_response = http_response_data[string_start:string_end].strip()
        except IndexError:
            server_response = ""

        try:
            string_start = http_response_data.lower().find("content-type:")
            if not string_start == -1:
                string_end = http_response_data.find("\\x00", string_start)
                content_type = http_response_data[string_start:string_end].split(":", 1)[1].strip()
                if ";" in content_type:
                    content_type = content_type.split(";", 1)[0].strip()
        except IndexError:
            content_type = ""

        try:
            string_start = http_response_data.lower().find("etag:")
            if not string_start == -1:
                string_end = http_response_data.find("\\x00", string_start)
                etag = http_response_data[string_start:string_end].split(":", 1)[1].strip()
        except IndexError:
            etag = ""

        try:
            string_start = http_response_data.lower().find("date:")
            if not string_start == -1:
                string_end = http_response_data.find("\\x00", string_start)
                response_time = http_response_data[string_start:string_end].split(":", 1)[1].strip()
                if not response_time == "":
                    response_time, timezone = time_convert(response_time, timezone)
        except IndexError:
            response_time = ""
            timezone = ""

        try:
            string_start = http_response_data.lower().find("last-modified:")
            if not string_start == -1:
                string_end = http_response_data.find("\\x00", string_start)
                last_modified = http_response_data[string_start:string_end].split(":", 1)[1].strip()
                if not last_modified == "":
                    last_modified, timezone = time_convert(last_modified, timezone)
        except IndexError:
            last_modified = ""
            timezone = ""

        try:
            string_start = http_response_data.lower().find("max-age=")
            if not string_start == -1:
                string_end = http_response_data.find("\\x00", string_start)
                max_age = http_response_data[string_start:string_end].split("=", 1)[1].split(",", 1)[0].strip()
        except IndexError:
            max_age = ""

        try:
            string_start = http_response_data.lower().find("server:")
            if not string_start == -1:
                string_end = http_response_data.find("\\x00", string_start)
                server_name = http_response_data[string_start:string_end].split(":", 1)[1].strip()
        except IndexError:
            server_name = ""

        try:
            string_start = http_response_data.lower().find("expires:")
            if not string_start == -1:
                string_end = http_response_data.find("\\x00", string_start)
                expire_time = http_response_data[string_start:string_end].split(":", 1)[1].strip()
                if not expire_time == "":
                    expire_time, timezone = time_convert(expire_time, timezone)
        except IndexError:
            expire_time = ""
            timezone = ""

        try:
            string_start = http_response_data.lower().find("content-encoding:")
            if not string_start == -1:
                string_end = http_response_data.find("\\x00", string_start)
                content_encoding = http_response_data[string_start:string_end].split(":", 1)[1].strip()
        except IndexError:
            content_encoding = ""

        try:
            server_ip = findall(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}", http_response_data)[0].strip()
        except IndexError:
            server_ip = ""

    return server_response, content_type, etag, response_time, last_modified, max_age, server_name, expire_time, \
        timezone, content_encoding, server_ip


def month_convert(month):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_num = str("{:02d}".format(months.index(month) + 1))
    return month_num


def time_convert(time, timezone):
    old_time = time.split(" ")
    if len(old_time) < 5:
        new_time = ""
    else:
        if "origin" in old_time[0].lower():
            old_time.insert(0, "")
        date = old_time[1] + "/" + month_convert(old_time[2]) + "/" + old_time[3]
        new_time = date + " " + old_time[4]
        if timezone == "":
            timezone = old_time[5]
    return new_time, timezone


def content_to_file(resource_data, filename, file_extension, output_dir, content_encoding, url_data, content_type):
    fullname = ""
    md5 = ""
    sha1 = ""
    sha256 = ""

    if r"/messages?" in url_data:
        extracted_dir = join(output_dir, "Extracted", "Chat_logs")
    elif "image" in content_type:
        extracted_dir = join(output_dir, "Extracted", "Images")
    elif "audio" in content_type:
        extracted_dir = join(output_dir, "Extracted", "Audio")
    elif "video" in content_type:
        extracted_dir = join(output_dir, "Extracted", "Video")
    else:
        extracted_dir = join(output_dir, "Extracted", "Other")

    # If gzip compression is detected decompress the data
    if content_encoding == "gzip":
        resource_data = decompress(resource_data)
    # Brotli is not supported by python3. Use separate script or tool to decode file encoded in brotli
    # Currently extensions are changed for all brotli compressed files
    elif content_encoding == "br":
        file_extension = ".br"

    # Write resource data to a new file
    i = 0
    if resource_data is not None:
        if exists(join(extracted_dir, filename + file_extension)):
            # If filename already exists in the folder add appropriate number
            while exists(join(extracted_dir, filename + f" ({i})" + file_extension)):
                i += 1
            with open(join(extracted_dir, filename + f" ({i})" + file_extension), "wb") as file:
                file.write(resource_data)
            fullname = f"{filename} ({i}){file_extension}"
        else:
            with open(join(extracted_dir, filename + file_extension), "wb") as file:
                file.write(resource_data)
            fullname = f"{filename}{file_extension}"

        # Setting block size might increase the calculation speed for larger files
        blocksize = 65536
        md5_hasher = hashlib.md5()
        sha1_hasher = hashlib.sha1()
        sha256_hasher = hashlib.sha256()
        with open(join(extracted_dir, fullname), "rb") as calc:
            buf = calc.read(blocksize)
            # Calculate MD5, SHA1 and SHA256 hash values
            while len(buf) > 0:
                md5_hasher.update(buf)
                sha1_hasher.update(buf)
                sha256_hasher.update(buf)
                buf = calc.read(blocksize)
        # Save values for further use
        md5 = md5_hasher.hexdigest()
        sha1 = sha1_hasher.hexdigest()
        sha256 = sha256_hasher.hexdigest()
    return fullname, md5, sha1, sha256
