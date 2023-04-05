import base64
import os
import re
import sys
import time

import requests
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy

capabilities = {
    "platformName": "android",
    "appium:app": sys.argv[1],
    "appium:autoGrantPermissions": True,
    "appium:automationName": "uiautomator2",
    "appium:deviceName": "emulator-5554",
    "appium:fullReset": False,
    "appium:noReset": True,
    "appium:noSign": True,
}

prefix = "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/androidx.recyclerview.widget.RecyclerView"


def send_to_telegram(message, file_opened, api_token, chat_id):
    try:
        if file_opened:
            response = requests.post(
                f"https://api.telegram.org/bot{api_token}/sendPhoto",
                {"chat_id": chat_id, "caption": message, "parse_mode": "HTML"},
                files={"photo": file_opened},
            )
        else:
            response = requests.post(
                f"https://api.telegram.org/bot{api_token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                },
            )
        print(response.text)
    except Exception as e:
        print(e)


def send_to_telegram_full(message, file_opened):
    send_to_telegram(
        message,
        file_opened,
        os.environ.get("TG_BOT_API_TOKEN"),
        "-1001920884298",
    )


def send_to_telegram_hk(message, file_opened):
    send_to_telegram(
        message,
        file_opened,
        os.environ.get("TG_BOT_API_TOKEN"),
        "-1001931323142",
    )


def send_to_telegram_tw(message, file_opened):
    send_to_telegram(
        message,
        file_opened,
        os.environ.get("TG_BOT_API_TOKEN"),
        "-1001804211083",
    )


def check_if_send_to_telegram(el_name, el_address, el_image, msgs, func):
    this_tuple = (el_name.text, el_address.text)
    print(this_tuple)

    if any(item == this_tuple for item in msgs):
        print("===== SAME RESULT =====")
    else:
        pattern = re.compile("座標: (\d+\.\d+), (\d+\.\d+)")
        formatted_msg = re.sub(
            pattern,
            r'座標: <a href="https://maps.google.com/?q=\1,\2">\1, \2</a>',
            f"{el_name.text}\n{el_address.text}\n\n",
        )

        img_file = open("image.png", "wb")
        img_file.write(base64.b64decode(el_image.screenshot_as_base64))
        img_file.close()

        with open("image.png", "rb") as img_file:
            func(formatted_msg, img_file)

        msgs.append(this_tuple)


def run():
    full_msgs = []
    hk_msgs = []
    tw_msgs = []

    try:
        driver = webdriver.Remote("http://localhost:4723/wd/hub", capabilities)

        el = driver.find_element(
            by=AppiumBy.ID, value="com.daydreamer.wecatch:id/fab_track"
        )
        el.click()

        send_to_telegram_full("=== 開機 ===", None)
        send_to_telegram_hk("=== 開機 ===", None)
        send_to_telegram_tw("=== 開機 ===", None)

        for y in range(1, 500):
            el = driver.find_element(
                by=AppiumBy.XPATH,
                value=f"{prefix}/android.widget.LinearLayout[1]/android.widget.LinearLayout/android.widget.TextView",
            )
            el.click()

            # wait the list load
            time.sleep(30)

            for x in range(1, 4):
                layout_xpath = f"{prefix}/android.widget.LinearLayout[{x}]/android.widget.LinearLayout"
                layout_2_xpath = f"{layout_xpath}/android.widget.LinearLayout"

                el_name = driver.find_element(
                    by=AppiumBy.XPATH,
                    value=f"{layout_2_xpath}/android.widget.TextView[1]",
                )

                el_address = driver.find_element(
                    by=AppiumBy.XPATH,
                    value=f"{layout_2_xpath}/android.widget.TextView[2]",
                )

                el_image = driver.find_element(
                    by=AppiumBy.XPATH,
                    value=f"{layout_xpath}//android.widget.ImageView",
                )

                check_if_send_to_telegram(
                    el_name,
                    el_address,
                    el_image,
                    full_msgs,
                    send_to_telegram_full,
                )

                if "香港" in el_address.text:
                    check_if_send_to_telegram(
                        el_name,
                        el_address,
                        el_image,
                        hk_msgs,
                        send_to_telegram_hk,
                    )

                elif "台灣" in el_address.text:
                    check_if_send_to_telegram(
                        el_name,
                        el_address,
                        el_image,
                        tw_msgs,
                        send_to_telegram_tw,
                    )

            # wait to view the list
            time.sleep(30)

            driver.back()

            # wait to restart
            time.sleep(30)

    except Exception as e:
        print(e)

    finally:
        driver.quit()
        send_to_telegram_full("=== 關機 ===", None)
        send_to_telegram_hk("=== 關機 ===", None)
        send_to_telegram_tw("=== 關機 ===", None)


run()
