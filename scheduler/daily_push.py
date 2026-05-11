from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

async def start_scheduler(bot):

    async def daily():
        print("🌙 Daily spiritual scheduler active")

    scheduler.add_job(daily, "interval", hours=24)

    scheduler.start()