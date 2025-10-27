from django.db.models.signals import pre_save
from django.dispatch import receiver
from config.settings import TELEGRAM_BOT_TOKEN
from .models import Order
import requests


@receiver(pre_save, sender=Order)
def send_order_status_notification(sender, instance, **kwargs):
    """
    Order modeli statusi o'zgarganda Telegram orqali foydalanuvchiga habar yuboradi.
    """
    # Yangi order emasligini tekshiramiz (faqat update paytida)
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    # Agar status o‘zgarmagan bo‘lsa, hech narsa qilmaymiz
    if old_instance.status == instance.status:
        return

    user = instance.user
    telegram_id = user.telegram_id
    if not telegram_id:
        return  # agar foydalanuvchida telegram_id bo‘lmasa, xabar yuborilmaydi

    # Foydalanuvchi tili
    lang = user.language or "uz"

    # Xabar matnlari
    messages = {
        "uz": {
            "preparing": "🍳 Buyurtmangiz tayyorlanmoqda.",
            "delivering": "🚚 Buyurtmangiz yo‘lda.",
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

    # Telegram xabar yuborish
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
