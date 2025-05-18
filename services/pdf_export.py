from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import os
import io
import matplotlib.pyplot as plt
import numpy as np
from services.stats import get_all_users, get_all_purchases
from scipy.stats import chi2_contingency, fisher_exact

pdfmetrics.registerFont(TTFont('DejaVuSans', 'D:\\Diplom\\DejaVuSans.ttf'))

def get_user_stats_data():
    users = get_all_users()
    total_users = len(users)
    active_users = sum(1 for user in users if user.get('active'))
    percent_active = round((active_users / total_users) * 100, 2) if total_users > 0 else 0

    weekday_counts = [0] * 7
    for user in users:
        if 'created_at' in user:
            dt = datetime.fromisoformat(user['created_at'])
            weekday_counts[dt.weekday()] += 1

    stats_text = (
        f"📊 Общая статистика пользователей:\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"✅ Активных: {active_users} ({percent_active}%)\n"
    )
    return stats_text, users, weekday_counts

def get_purchase_stats():
    purchases = get_all_purchases()
    if not purchases:
        return "Нет данных о покупках.", [], {}, 0

    prices = [p['price'] for p in purchases]
    avg_price = round(sum(prices) / len(prices), 2)
    max_price = max(prices)
    min_price = min(prices)

    product_count = {}
    user_purchase_counts = {}

    for p in purchases:
        pid = p['product_id']
        uid = p['user_id']
        product_count[pid] = product_count.get(pid, 0) + 1
        user_purchase_counts[uid] = user_purchase_counts.get(uid, 0) + 1

    repeat_ratio = round(
        (sum(1 for count in user_purchase_counts.values() if count > 1) / len(user_purchase_counts)) * 100, 2
    ) if user_purchase_counts else 0

    stats_text = (
        f"\n🛒 Статистика покупок:\n"
        f"📈 Средняя цена: {avg_price} BYN\n"
        f"💰 Мин. цена: {min_price} BYN, Макс. цена: {max_price} BYN\n"
        f"📦 Куплено товаров: {len(purchases)}\n"
        f"🔢 Уникальных товаров: {len(product_count)}\n"
        f"🔁 Повторных покупателей: {repeat_ratio}%"
    )
    return stats_text, prices, product_count, repeat_ratio

def plot_bar_chart(values, labels, title, xlabel, ylabel):
    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color='skyblue', edgecolor='black')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

def plot_histogram(data, title, xlabel, ylabel):
    plt.figure(figsize=(6, 4))
    plt.hist(data, bins=15, color='skyblue', edgecolor='black')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

def plot_pie_chart(active_count, inactive_count):
    plt.figure(figsize=(4, 4))
    plt.pie(
        [active_count, inactive_count],
        labels=["Активные", "Неактивные"],
        autopct='%1.1f%%',
        colors=['#4CAF50', '#FF5722']
    )
    plt.title("Активность пользователей")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

def calc_chi2_and_fisher(users, purchases):
    buyers = set(p['user_id'] for p in purchases)

    active_with_purchase = 0
    active_without_purchase = 0
    inactive_with_purchase = 0
    inactive_without_purchase = 0

    for user in users:
        uid = user.get('id')
        is_active = user.get('active', False)
        has_purchase = uid in buyers

        if is_active and has_purchase:
            active_with_purchase += 1
        elif is_active and not has_purchase:
            active_without_purchase += 1
        elif not is_active and has_purchase:
            inactive_with_purchase += 1
        elif not is_active and not has_purchase:
            inactive_without_purchase += 1

    contingency_table = np.array([
        [active_with_purchase, active_without_purchase],
        [inactive_with_purchase, inactive_without_purchase]
    ])

    if np.any(contingency_table == 0):
        contingency_table = contingency_table + 0.5

    chi2, p_chi2, _, _ = chi2_contingency(contingency_table)
    _, p_fisher = fisher_exact(contingency_table)

    return chi2, p_chi2, p_fisher, contingency_table.tolist()

def ensure_space(c, y_pos, required_space, margin, height):
    if y_pos - required_space < margin:
        c.showPage()
        c.setFont("DejaVuSans", 12)
        return height - margin
    return y_pos

def export_stats_to_pdf():
    file_path = "data/Отчёт о пользователях Телеграмм бота.pdf"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    margin = 50
    y_pos = height - margin

    c.setFont("DejaVuSans", 14)

    stats_text, users, weekday_counts = get_user_stats_data()
    for line in stats_text.strip().split('\n'):
        y_pos = ensure_space(c, y_pos, 20, margin, height)
        c.drawString(margin, y_pos, line)
        y_pos -= 20

    day_labels = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    hist_buf = plot_bar_chart(weekday_counts, day_labels, "Регистрации по дням недели", "День", "Количество")
    hist_img = ImageReader(hist_buf)
    img_width = width - 2 * margin
    img_height = img_width * 0.66
    y_pos = ensure_space(c, y_pos, img_height + 10, margin, height)
    y_pos -= img_height + 10
    c.drawImage(hist_img, margin, y_pos, width=img_width, height=img_height)

    active_count = sum(1 for u in users if u.get('active'))
    inactive_count = len(users) - active_count
    pie_buf = plot_pie_chart(active_count, inactive_count)
    pie_img = ImageReader(pie_buf)
    pie_size = 200
    y_pos = ensure_space(c, y_pos, pie_size + 30, margin, height)
    y_pos -= pie_size + 30
    c.drawImage(pie_img, margin + (img_width - pie_size)/2, y_pos, width=pie_size, height=pie_size)

    c.setFont("DejaVuSans", 12)
    purchase_text, prices, product_count, repeat_ratio = get_purchase_stats()
    for line in purchase_text.strip().split('\n'):
        y_pos = ensure_space(c, y_pos, 18, margin, height)
        y_pos -= 18
        c.drawString(margin, y_pos, line)

    if prices:
        price_buf = plot_histogram(prices, "Распределение цен покупок", "Цена (BYN)", "Количество")
        price_img = ImageReader(price_buf)
        y_pos = ensure_space(c, y_pos, img_height + 10, margin, height)
        y_pos -= img_height + 10
        c.drawImage(price_img, margin, y_pos, width=img_width, height=img_height)

    purchases = get_all_purchases()
    chi2, p_chi2, p_fisher, table = calc_chi2_and_fisher(users, purchases)

    y_pos = ensure_space(c, y_pos, 40, margin, height)
    y_pos -= 40
    c.setFont("DejaVuSans", 12)
    c.drawString(margin, y_pos, "📈 Статистические тесты:")
    y_pos -= 18

    data = [["", "Покупал", "Не покупал"],
            ["Активные", str(table[0][0]), str(table[0][1])],
            ["Неактивные", str(table[1][0]), str(table[1][1])]]

    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'DejaVuSans'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ])

    t = Table(data)
    t.setStyle(table_style)
    y_pos = ensure_space(c, y_pos, 80, margin, height)
    t.wrapOn(c, width - 2*margin, 60)
    t.drawOn(c, margin, y_pos - 60)
    y_pos -= 60

    y_pos = ensure_space(c, y_pos, 48, margin, height)
    y_pos -= 30
    c.drawString(margin, y_pos, f"Хи-квадрат: {chi2:.4f}, p-value: {p_chi2:.4f}")
    y_pos -= 18
    c.drawString(margin, y_pos, f"Тест Фишера p-value: {p_fisher:.4f}")

    c.save()
    return file_path
