from django.db.models.signals import pre_save
from django.dispatch import receiver
from config.settings import TELEGRAM_BOT_TOKEN, ADMIN_TELEGRAM_ID
from .models import Order
import requests
from django.db.models.signals import post_save
from .models import Product
from decimal import Decimal
from django.db import transaction
import sys


@receiver(pre_save, sender=Order)
def send_order_status_notification(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if old_instance.status == instance.status:
        return

    user = instance.user
    telegram_id = user.telegram_id
    if not telegram_id:
        return

    lang = user.language or "uz"

    messages = {
        "uz": {
            "preparing": "🍳 Buyurtmangiz kutilmoqda",
            "delivering": "🚚 Buyurtmangiz qabul qilindi",
            "completed": "✅ Buyurtmangiz yakunlandi!",
            "cancelled": "❌ Buyurtmangiz bekor qilindi.",
        },
        "ru": {
            "preparing": "🍳 Ваш заказ готовится.",
            "delivering": "🚚 Ваш заказ в пути.",
            "completed": "✅ Ваш заказ завершён!",
            "cancelled": "❌ Ваш заказ отменён.",
        },
    }

    msg = messages.get(lang, messages["uz"]).get(instance.status, "📦 Buyurtma holati o‘zgardi.")

    token = TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": telegram_id,
        "text": msg,
    }

    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram xabar yuborishda xatolik: {e}")


@receiver(post_save, sender=Product)
def notify_low_stock(sender, instance, **kwargs):
    def send_notification():
        try:
            sys.stdout.reconfigure(encoding='utf-8')

            product = Product.objects.select_related('name_category__category').get(pk=instance.pk)

            quantity_value = Decimal(str(product.quantity))
            if quantity_value <= Decimal('5.00'):
                category_name = product.name_category.category.name
                type_name = product.name_category.name
                product_name = product.name
                quantity = product.quantity

                # ✨ Emoji'lar bilan xabar
                message = (
                    "⚠️ *Omborda mahsulot kamaydi!*\n\n"
                    f"📂 *Kategoriya:* {category_name}\n"
                    f"🏷️ *Turi:* {type_name}\n"
                    f"🥫 *Nomi:* {product_name}\n"
                    f"📉 *Qolgan miqdor:* {quantity} {product.unit}"
                )

                token = TELEGRAM_BOT_TOKEN
                chat_id = ADMIN_TELEGRAM_ID
                url = f"https://api.telegram.org/bot{token}/sendMessage"

                payload = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }

                response = requests.post(url, json=payload, timeout=5)
                print(f"Telegram javobi: {response.status_code}")

            else:
                print(f"{product.name} yetarli miqdorda ({product.quantity}), xabar yuborilmadi.")

        except Exception as e:
            print(f"Low stock signal xatolik: {e}".encode("utf-8", errors="ignore").decode("utf-8"))

    conn = transaction.get_connection()
    if conn.in_atomic_block:
        print("Transaction ichida, commitdan keyin bajariladi.")
        conn.on_commit(send_notification)
    else:
        print("Transaction yo‘q, darhol bajariladi.")
        send_notification()
