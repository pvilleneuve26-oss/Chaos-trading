  GNU nano 8.7.1           bot.py
import discord
import aiohttp
import asyncio
import time

TOKEN = "TOKEN"
TORN_API_KEY = "TORN_KEY"

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

ITEM_CACHE = {}
PRICE_CACHE = {}
CACHE_DURATION = 60


# -------- LOAD ITEMS -------- #

async def load_items():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.torn.com/torn/?selections=i>
        ) as resp:
            data = await resp.json()

            if "error" in data:
                print("Torn API Error:", data["error">
                return

            for item_id, item_data in data["items"].i>
                ITEM_CACHE[item_data["name"].lower()]>

    print(f"Loaded {len(ITEM_CACHE)} items.")


# -------- GET MARKET PRICE -------- #

async def get_market_price(item_id):
    current_time = time.time()

    if item_id in PRICE_CACHE:
        lowest, avg, count, timestamp = PRICE_CACHE[i>
        if current_time - timestamp < CACHE_DURATION:
            return lowest, avg, count

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.torn.com/v2/market/{item_id>
        ) as resp:

            data = await resp.json()

            if "error" in data:
                print("Torn API Error:", data["error">
                return None, None, 0

            if "itemmarket" not in data:
                print("Unexpected structure:", data)
                return None, None, 0

            itemmarket = data["itemmarket"]

            if "listings" not in itemmarket:
                print("Missing listings:", itemmarket)
                return None, None, 0

            listings = itemmarket["listings"]

            if not listings:
                return None, None, 0

            prices = [l["price"] for l in listings]

            lowest = min(prices)
            avg = int(sum(prices) / len(prices))
            count = len(prices)

            PRICE_CACHE[item_id] = (lowest, avg, coun>

            return lowest, avg, count

            # ---- HANDLE DIFFERENT POSSIBLE STRUCTUR>

            listings = []

            # Structure option 1
            if isinstance(itemmarket, dict) and "item>
                item_data = itemmarket["item"]
                if "listings" in item_data:
                    listings = item_data["listings"]

            # Structure option 2 (flat listings)
            if isinstance(itemmarket, list):
                listings = itemmarket

            # If still empty, inspect
            if not listings:
                print("Unknown itemmarket structure:">
                return None, None, 0

            prices = [l["price"] for l in listings if>

            if not prices:
                return None, None, 0

            lowest = min(prices)
            avg = int(sum(prices) / len(prices))
            count = len(prices)

            PRICE_CACHE[item_id] = (lowest, avg, coun>

            return lowest, avg, count


# -------- READY -------- #

@bot.event
async def on_ready():
    print("Loading Torn items...")
    await load_items()

    for guild in bot.guilds:
        await tree.sync(guild=guild)
        print(f"Synced commands to {guild.name}")

    print("Bot is ready.")


# -------- SLASH COMMAND -------- #

@tree.command(name="price", description="Get Torn mar>
async def price(interaction: discord.Interaction, ite>

    await interaction.response.defer()

    item_lower = item.lower()

    if item_lower not in ITEM_CACHE:
        await interaction.followup.send("❌ Item not >
        return

    item_id = ITEM_CACHE[item_lower]
    lowest, avg, count = await get_market_price(item_>

    if lowest is None:
        await interaction.followup.send("No market li>
        return

    embed = discord.Embed(
        title=f"{item.title()} Market Price",
        color=discord.Color.green()
    )

    embed.add_field(name="Lowest", value=f"${lowest:,>
    embed.add_field(name="Average", value=f"${avg:,}">
    embed.add_field(name="Listings", value=str(count)>

    await interaction.followup.send(embed=embed)


bot.run(TOKEN)
