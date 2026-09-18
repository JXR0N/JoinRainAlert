import asyncio
import os
import sys
import logging

from time import time as now
from playwright.async_api import async_playwright, expect
from asyncio import sleep
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def loadTargetUser(bot):
    try:
        user = await bot.fetch_user("enter target here")
        logging.info("Fetched user successfully")
        return user
    except Exception as e:
        logger.error("Error while fetching target user")


async def clearBrowsers(browserList):
    if len(browserList) == 0:
        return
    temp_browser_amount = len(browserList)
    for browser_element in browserList:
        await browser_element.close()
    browserList.clear()
    logger.info(f"List of browsers have been cleared. {temp_browser_amount} browsers were closed.")

async def searchJoinRain(page, temp):
    try:
        await expect(page.get_by_role("button", name="Join Rain")).to_be_visible()
        return True, temp
    except (AssertionError, Exception):
        return False, True


async def sendAlert(temp, bot):
    if temp:
        user = await loadTargetUser(bot)
        logger.info("Alert has been send to user")
        
        for i in range(5):
            await sleep(1)
            await user.send("Rain Drop Event Alert 🚨!!!")
        return False

    else:
        return temp

async def launchBrowser(p, browserList = []):
    await clearBrowsers(browserList)

    goal_time = now() + 1800
    browser = await p.chromium.launch(headless=True, slow_mo=100)
    browserList.append(browser)
    page = await browser.new_page()
    await page.goto("https://donutluck.com/")

    return goal_time, True, page


async def mainListener(bot):
    try:
        async with async_playwright() as p:

            goal_time, temp, page = await launchBrowser(p)

            while True:

                if now() >= goal_time:
                    goal_time = now() + 1800
                    goal_time, temp, page = await launchBrowser(p)

                await sleep(3)

                result, temp = await searchJoinRain(page, temp)
                if(result):
                    temp = await sendAlert(temp, bot)
    except Exception:
        logger.error("Browser crashed")
        return True
        
