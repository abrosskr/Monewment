# .FIS Protocol (FOT Interface Standard)
# Version: 1.0.0
# Description: Low-level binary-to-json mapping for device communication.

FIS_PACKET_SCHEMA = {
    "header": "0xFE",
    "payload_type": "string",
    "payload_data": "bytes",
    "checksum": "uint16"
}

# Module Interface Standard
OMNI_CRAWLER_INTERFACE = {
    "endpoints": ["/crawl/logistics", "/crawl/price", "/crawl/recipe"],
    "output_format": "JSON_BUFFER",
    "storage_policy": "ASYNC_APPEND"
}
