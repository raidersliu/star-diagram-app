
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import math
import io

def split_and_sum(date_str):
    digits = [int(ch) for ch in date_str if ch.isdigit()]
    total = sum(digits)
    if date_str[0] == '2':
        total += 18
    return digits, total

def reduce_to_single_digit(n):
    while n > 10:
        n = sum(int(d) for d in str(n))
    return n

def get_type_chain(start_type, steps):
    if start_type == 10:
        return [((start_type + i + 1) % 10) + 1 for i in range(steps)]
    else:
        return [((start_type + i - 1) % 10) + 1 for i in range(steps + 1)]

def count_10_components(date_str):
    year = int(date_str[2:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    return sum(1 for val in [year, month, day] if val % 10 == 0)

def sum_mmdd_digits(date_str):
    mmdd = date_str[4:8]
    digits = [int(d) for d in mmdd]
    summ = sum(digits)
    while summ > 10:
        summ = sum(int(d) for d in str(summ))
    return summ

def analyze_date_code(date_str):
    yy = date_str[2:4]
    mm = date_str[4:6]
    dd = date_str[6:8]
    combined_digits = yy + mm + dd
    digit_count = {str(i): 0 for i in range(1, 11)}
    for ch in combined_digits:
        if ch in digit_count:
            digit_count[ch] += 1
    digit_count["10"] = sum(1 for x in [yy, mm, dd] if int(x) % 10 == 0)
    return digit_count

def modify_code(date_str, digit_count):
    yy = int(date_str[2:4])
    mm = int(date_str[4:6])
    dd = int(date_str[6:8])
    aaa = sum([1 for v in [yy, mm, dd] if v == 10])
    digit_count["1"] = str(int(digit_count["1"]) - aaa)
    return digit_count

def calculate_star_type(birthday_str):
    digits, total_sum = split_and_sum(birthday_str)
    simplified = reduce_to_single_digit(total_sum)
    ten_count = count_10_components(birthday_str)
    personality = sum_mmdd_digits(birthday_str)
    result = {
        "生日": birthday_str,
        "原始加總": total_sum,
        "轉換次數": ten_count,
        "類型 Type": simplified,
        "人格 Personality": personality,
        "星型類型變化": get_type_chain(simplified, ten_count),
        "成熟年齡": total_sum,
        "轉變年齡": [total_sum + 10 * i for i in range(1, ten_count + 1)]
    }
    return result, simplified

def draw_star_with_repeated_numbers(result, typen, digit_count):
    width, height = 800, 800
    center = (width // 2, height // 2)
    radius_outer = 250
    radius_inner = 100
    label_offset = 40
    layer_spacing = 10

    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    points = []
    for i in range(5):
        outer_angle = math.radians(90 + i * 72)
        inner_angle = math.radians(90 + i * 72 + 36)
        points.append((center[0] + radius_outer * math.cos(outer_angle),
                       center[1] - radius_outer * math.sin(outer_angle)))
        points.append((center[0] + radius_inner * math.cos(inner_angle),
                       center[1] - radius_inner * math.sin(inner_angle)))

    draw.line(points + [points[0]], fill='black', width=5)

    try:
        font = ImageFont.truetype("./MSJH.ttc", 12)
        font_center = ImageFont.truetype("./MSJH.ttc", 36)
        font_data = ImageFont.truetype("./MSJH.ttc", 18)
    except:
        font = ImageFont.load_default()
        font_center = ImageFont.load_default()
        font_data = ImageFont.load_default()

    numbers_with_counts = [(str(i), int(digit_count[str(i)])) for i in range(1, 11)]

    for idx, (px, py) in enumerate(points):
        number, count = numbers_with_counts[idx]
        number1, count1 = numbers_with_counts[(idx - 1 + typen) % 10]
        upper_text = f"({number1 * count1})" if count1 > 0 else " "
        lower_text = number * count if count > 0 else " "
        angle = math.atan2(py - center[1], px - center[0])
        base_x = px + label_offset * math.cos(angle)
        base_y = py + label_offset * math.sin(angle)
        draw.text((base_x, base_y - layer_spacing), upper_text, fill='red', font=font, anchor="mm")
        draw.text((base_x, base_y + layer_spacing), lower_text, fill='black', font=font, anchor="mm")

    draw.text(center, "T " + str(typen), fill='green', font=font_center, anchor="mm")
    # Add result summary text on the image
    zz = 0
    for k, v in result.items():
        draw.text((150, 100 + zz), f"{k}: {v}", fill='black', font=font_data, anchor="lm")
        zz += 20

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# Streamlit Interface
st.title("身體自覺 五星術分析與星型圖示 Penny")

birthday_input = st.text_input("請輸入生日 (格式: YYYYMMDD)", "20250519")

if st.button("執行分析與繪圖"):
    result, typen = calculate_star_type(birthday_input)
    digit_count = analyze_date_code(birthday_input)
    digit_count = modify_code(birthday_input, digit_count)
    st.subheader("分析結果")
    for key, value in result.items():
        st.write(f"{key}: {value}")

    st.subheader("星型圖示")
    star_image = draw_star_with_repeated_numbers(result, typen, digit_count)
    st.image(star_image, caption="您的星型圖示", use_column_width=False)
    st.download_button("下載圖像", star_image, file_name="star_diagram.png", mime="image/png")
