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
from services.stats import get_all_users
from scipy.stats import chi2_contingency, fisher_exact

pdfmetrics.registerFont(TTFont('DejaVuSans', 'D:\\Diplom\\DejaVuSans.ttf'))

def get_user_stats_data():
    users = get_all_users()
    total_users = len(users)
    active_users = sum(1 for user in users if user.get('active'))
    percent_active = round((active_users / total_users) * 100, 2) if total_users > 0 else 0
    now = datetime.now()
    account_ages = [
        (now - datetime.fromisoformat(user['created_at'])).days
        for user in users if 'created_at' in user
    ]
    avg_account_age = round(sum(account_ages) / len(account_ages), 2) if account_ages else 0
    stats_text = (
        f"📊 Общая статистика пользователей:\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"✅ Активных: {active_users} ({percent_active}%)\n"
        f"📆 Средний возраст аккаунта: {avg_account_age} дней\n"
    )
    return stats_text, users, account_ages

def plot_histogram(account_ages):
    plt.figure(figsize=(6, 4))
    plt.hist(account_ages, bins=20, color='skyblue', edgecolor='black')
    plt.title("Распределение возраста аккаунтов (в днях)")
    plt.xlabel("Возраст аккаунта (дни)")
    plt.ylabel("Количество пользователей")
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

def calc_chi2_and_fisher(users):
    active_and_a = sum(1 for u in users if u.get('active') and u.get('username', '').lower().startswith('a'))
    active_and_not_a = sum(1 for u in users if u.get('active') and not u.get('username', '').lower().startswith('a'))
    inactive_and_a = sum(1 for u in users if not u.get('active') and u.get('username', '').lower().startswith('a'))
    inactive_and_not_a = sum(1 for u in users if not u.get('active') and not u.get('username', '').lower().startswith('a'))

    contingency_table = np.array([
        [active_and_a, active_and_not_a],
        [inactive_and_a, inactive_and_not_a]
    ])

    if np.any(contingency_table == 0):
        contingency_table = contingency_table + 0.5

    chi2, p_chi2, _, _ = chi2_contingency(contingency_table)
    _, p_fisher = fisher_exact(contingency_table)

    return chi2, p_chi2, p_fisher, contingency_table.tolist()

def export_stats_to_pdf():
    file_path = "data/Отчёт о пользователях Телеграмм бота .pdf"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    margin = 50
    y_pos = height - margin

    c.setFont("DejaVuSans", 14)

    stats_text, users, account_ages = get_user_stats_data()
    for line in stats_text.strip().split('\n'):
        c.drawString(margin, y_pos, line)
        y_pos -= 20

    # Вставляем гистограмму
    hist_buf = plot_histogram(account_ages)
    hist_img = ImageReader(hist_buf)
    img_width = width - 2*margin
    img_height = img_width * 0.66  # соотношение 6:4
    y_pos -= img_height + 10
    c.drawImage(hist_img, margin, y_pos, width=img_width, height=img_height)

    # Вставляем круговую диаграмму
    active_count = sum(1 for u in users if u.get('active'))
    inactive_count = len(users) - active_count
    pie_buf = plot_pie_chart(active_count, inactive_count)
    pie_img = ImageReader(pie_buf)
    pie_size = 200
    y_pos -= pie_size + 30
    c.drawImage(pie_img, margin + (img_width - pie_size)/2, y_pos, width=pie_size, height=pie_size)

    y_pos -= 30

    # Статистические тесты
    chi2, p_chi2, p_fisher, table = calc_chi2_and_fisher(users)

    c.setFont("DejaVuSans", 12)
    c.drawString(margin, y_pos, "📈 Статистические тесты:")
    y_pos -= 18

    # Рисуем таблицу сопряженности
    data = [["", "Начинаются с 'a'", "Не начинаются с 'a'"],
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
    # Вычисляем высоту таблицы (3 строки по 18 пикселей)
    table_width = width - 2*margin
    table_height = 54
    t.wrapOn(c, table_width, table_height)
    y_pos -= table_height
    t.drawOn(c, margin, y_pos)

    y_pos -= 30
    c.drawString(margin, y_pos, f"Хи-квадрат: {chi2:.4f}, p-value: {p_chi2:.4f}")
    y_pos -= 18
    c.drawString(margin, y_pos, f"Тест Фишера p-value: {p_fisher:.4f}")

    c.save()
    return file_path
