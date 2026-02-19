# OMNI-CRAWLER Pipeline Design (MONEWMENT 1)
# Role: Fuel Line for VENDORS

## 1. Data Sources
- **Logistics**: Baemin (Logistics data)
- **Price**: Coupang (Market price data)
- **Recipe**: YouTube/Blog (Recipe metadata)

## 2. Pipeline Architecture (Decoupled & Async)
1. **Fetcher**: Uses `httpx` or `playwright` for async data retrieval.
2. **Sanitizer**: Cleans HTML/Raw JSON into MONEWMENT standard JSON.
3. **Buffer Manager**: Uses `aiofiles` to write to `data/buffer/` without blocking.
   - Path: `modules/omni_crawler/data/buffer/[YYYYMMDD]_[SOURCE].json`

## 3. Storage Rule
- **No DB Connection**: Directly writing to file systems ensures speed and isolation.
- **Atomic Writes**: JSON objects are written as single lines or separate files to prevent corruption.

## 4. Consumption (The Inter-Process Bridge)
- **API Gateway**: VENDORS module requests data via MONEWMENT 1 Gateway.
- **Stream**: MONEWMENT 1 reads from buffer and streams JSON to VENDORS over HTTP/TCP.
