# Image First OCR Discipline

## Trigger

Use this skill automatically whenever Hòa Đại ka sends, references, attaches, forwards, or asks about any image/screenshot/photo/scan/chart/map/document image, including:

- Telegram/WhatsApp/Discord images
- screenshots of websites/apps/errors/charts
- scanned giấy tờ, bản vẽ, GCN, quy hoạch, pháp lý, tài chính
- photos containing text, tables, map labels, coordinates, numbers, signatures, stamps
- images embedded in PDFs/docs when the question depends on visual content

## Hard Rule

**Never answer from guesswork when an image is available. Read the image first.**

If Hòa Đại ka sends an image, Tiểu đệ must inspect the actual image content before making claims, extracting numbers, summarizing, diagnosing, or answering what it means.

Do not rely only on:

- filename
- caption
- prior chat context
- memory
- nearby text
- assumptions about common templates
- “looks like probably...” reasoning without visual inspection

## Required Workflow

1. **Open/read the image file.**
   - Use available image-reading tools first.
   - If the image is in inbound media, read the actual local path.
   - If multiple images are sent, inspect each relevant image.

2. **OCR and visual inspection are both required when text matters.**
   - Read visible text directly where possible.
   - Use OCR tools/scripts if the built-in image read is insufficient.
   - Zoom/crop/enhance/rotate when text is small, blurry, sideways, low contrast, or partially cut.

3. **For tables/numbers/charts/maps:**
   - Extract exact visible values and labels.
   - State uncertainty when a value is unclear.
   - Do not invent hidden rows/columns/legend values.
   - If needed, crop table areas or chart axes before answering.

4. **For screenshots/errors/UI:**
   - Read the visible error/message/status text.
   - Identify the exact UI/page/app shown.
   - Do not diagnose from memory before checking the screenshot.

5. **For legal/finance/property documents:**
   - Treat OCR as evidence collection, not final truth.
   - Quote key visible phrases/numbers when useful.
   - Flag illegible fields instead of guessing.

6. **If image reading fails:**
   - Say clearly that the image could not be read and why.
   - Ask Hòa Đại ka to resend higher resolution or provide a closer crop.
   - Do not answer as if the image was read.

## Anti-Laziness Checklist

Before replying to an image-based request, confirm internally:

- Did I actually open/read the image file?
- Did I OCR/crop/zoom if the visible text was small or unclear?
- Did I avoid using stale context as a substitute for seeing the image?
- Did I mark uncertain/illegible parts instead of guessing?

If any answer is “no”, keep working before replying.

## Output Standard

When answering from an image, be explicit and evidence-based:

- “Em đọc trong ảnh thấy...”
- “Dòng/ô này ghi...”
- “Phần này mờ, em chưa chắc...”
- “Ảnh này không đủ nét để đọc số..., anh gửi crop gần hơn giúp em.”

## Done Criteria

A response to an image task is only acceptable when:

- the actual image content was inspected;
- important text/numbers/visual elements were extracted from the image;
- uncertainty is disclosed;
- no unsupported inference replaces OCR/visual reading.
