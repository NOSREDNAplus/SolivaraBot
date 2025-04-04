import discord, threading, json
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.all()
client = commands.Bot(command_prefix='/', intents=intents)
requests = {}

async def getData() -> dict:
    """
    Gets dictionary of config in data.json
    """
    with open("data.json", "r") as f:
        d = json.load(f)
        f.close()
    del f
    return d
async def updateData(d:dict) -> None:
    """
    Buffers updates for 'data.json'
    """
    with open("data.json", "w") as f:
        json.dump(d, f, indent=6)
        f.close()
    del f
async def getPartyRegs(guild:discord.Guild) -> dict:
    o, v = [], {}
    async for i in client.get_guild(guild.id).get_channel(1353291286853062738).history():
            #gets all messages from politcal parties channel
            if client.get_guild(guild.id).get_member_named(i.author.name).get_role(1353292286984720465) != None:
                o.append(i.content)
    for i in o:
            #gets information from the discord messages
            pname = i.split("\n")[0].replace("#", "").strip()
            pfounder = guild.get_member(int(i.split("\n")[2].replace("Party Founder/Leader:", "").strip().replace("<", "").replace(">", "").replace("@", "")))
            pideology = i.split("\n")[3].replace("Party Ideology:", "").strip()
            pposition = i.split("\n")[4].replace("Political Position:", "").strip()
            v[pname] = {"founder": pfounder, "ideology": pideology, "position":pposition} #adds information into a dictionary
    return v # returns dictionary data
#commands
@client.command(name="party")
async def party(ctx:commands.Context, *args):
    if args[0].lower() == "view":
        d = await getData()
        partyRegs = await getPartyRegs(ctx.guild)
        formatedResp = "## Political Parties\n"
        for i in partyRegs.items():
            formatedResp += f"- **{i[0]}** Founder: `{i[1]["founder"]}` Ideology: `{i[1]["ideology"]}` Political Position: `{i[1]["position"]}`\n"
            #checks if data is in data.json
            if not i[0] in d["parties"]:
                d["parties"][pname] = {"details": "", "joins": "Open"}
            #checks if data is in requests
            if not i[0] in requests.keys():
                requests[i[0]] = []
        for i in d['parties'].keys(): #deletes party data if not in Political Parties channel
            if not i in partyRegs.keys():
                del d['parties'][i]
        await updateData(d) #updates data.json file
        await ctx.reply(formatedResp) #sends formatted response
    elif args[0].lower() == "setdetails":
        partyRegs, partyData = [], {}
        async for i in client.get_guild(ctx.guild.id).get_channel(1353291286853062738).history():
            #gets all messages from politcal parties channel
            if client.get_guild(ctx.guild.id).get_member_named(i.author.name).get_role(1353292286984720465) != None:
                partyRegs.append(i.content)
        for i in partyRegs:
            #gets information from the discord messages
            pname = i.split("\n")[0].replace("#", "").strip()
            pfounder = ctx.guild.get_member(int(i.split("\n")[2].replace("Party Founder/Leader:", "").strip().replace("<", "").replace(">", "").replace("@", ""))).display_name
            partyData[pname] = pfounder
        if args[1] in partyData.keys():
            #checks if user is party owner
            if ctx.author.name == partyData[args[1]]:
                d = await getData()
                d['parties'][args[1]]['details'] = args[2]
                await updateData(d)
            else:
                await ctx.reply("> You have to be the party's founder to change its details!")
        else:
            await ctx.reply("> Part chosen doesn't exist!")
    elif args[0].lower() == "genrole":
        partyRegs, partyData = [], {}
        async for i in client.get_guild(ctx.guild.id).get_channel(1353291286853062738).history():
            #gets all messages from politcal parties channel
            if client.get_guild(ctx.guild.id).get_member_named(i.author.name).get_role(1353292286984720465) != None:
                partyRegs.append(i.content)
        for i in partyRegs:
            #gets information from the discord messages
            pname = i.split("\n")[0].replace("#", "").strip()
            pfounder = ctx.guild.get_member(int(i.split("\n")[2].replace("Party Founder/Leader:", "").strip().replace("<", "").replace(">", "").replace("@", ""))).display_name
            partyData[pname] = pfounder
        if args[1] in partyData.keys(): 
            #checks if user is party owner
           if ctx.author.display_name == partyData[args[1].strip()]:
                v = False
                serverRoles = await ctx.guild.fetch_roles()
                for i in serverRoles: #generates role if no role is already generated
                    if pname == i.name:
                        await ctx.reply("> Role already generated for this party!")
                        v = True
                        break
                if v == False:
                    role = await ctx.guild.create_role(name=pname, mentionable=True, reason=f"Role generated by user({ctx.author.name})")
                    await ctx.reply(f"> Successfully created role {role.mention}")
                    await ctx.author.add_roles(role)
           else:
               await ctx.reply("> You have to be the party's founder to generate its role!")
        else:
            await ctx.reply("> Party doesn't exist!")
    elif args[0].lower() == "details":
        d = await getData()
        if args[1] in d['parties'].keys():
            if d['parties'][args[1]]['details'] == "":
                await ctx.reply(f"## {args[1]} Details\nJoins: **{d['parties'][args[1]]['joins']}**\n-# Non.")
            else:
                await ctx.reply(f"## {args[1]} Details\n{d['parties'][args[1]]['details']}")
        else:
            await ctx.reply("Party doesn't exist!")
    elif args[0].lower() == "members":
        partyRegs = await getPartyRegs(ctx.guild)
        if args[1] in partyRegs.keys():
            role = None
            for i in await ctx.guild.fetch_roles():
                if i.name == args[1]:
                    role = i
                    break
            if role == None:
                await ctx.reply(f"Couldn't find role for desired party({args[1]})")
            else:
                formatedResp = f"## {args[1]} Party Members\n"
                for i in ctx.guild.members:
                    if i.get_role(role.id) != None:
                        formatedResp += f"- {i.display_name}\n"
                await ctx.reply(formatedResp)
        else:
            await ctx.reply(f"Party,{args[1]}, doesn't exist!")

    elif args[0].lower() == "setstatus":
        partyRegs, partyData = [], {}
        async for i in client.get_guild(ctx.guild.id).get_channel(1353291286853062738).history():
            #gets all messages from politcal parties channel
            if client.get_guild(ctx.guild.id).get_member_named(i.author.name).get_role(1353292286984720465) != None:
                partyRegs.append(i.content)
        for i in partyRegs:
            #gets information from the discord messages
            pname = i.split("\n")[0].replace("#", "").strip()
            pfounder = ctx.guild.get_member(int(i.split("\n")[2].replace("Party Founder/Leader:", "").strip().replace("<", "").replace(">", "").replace("@", ""))).display_name
            partyData[pname] = pfounder
        if args[1] in partyData.keys(): 
            #checks if user is party owner
           if ctx.author.display_name == partyData[args[1].strip()]:
                if args[2].lower() == "open" or args[1].lower() == "close":
                    d = await getData()
                    d["parties"][args[1]]["joins"] = args[2].lower()
                    await updateData()
                else:
                    await ctx.reply("> Invalid parameter, it has to be either `open` or `close`!")

           else:
               await ctx.reply("> You have to be the party's founder to generate its role!")
        else:
            await ctx.reply("> Party doesn't exist!")
    elif args[0].lower() == "join":
        d = await getData()
        if args[1] in d['parties'].keys():
            for i in d["parties"].keys():
                if not i in requests.keys():
                    requests[i] = []
            if d["parties"][args[1]]["joins"].lower() == "open":
                if ctx.author.id in requests[args[1]]:
                    await ctx.reply("> You've already sent a request to this party!")
                else:
                    partyRegs = [] 
                    async for i in client.get_guild(ctx.guild.id).get_channel(1353291286853062738).history():
                        #gets all messages from politcal parties channel
                        if client.get_guild(ctx.guild.id).get_member_named(i.author.name).get_role(1353292286984720465) != None:
                            partyRegs.append(i.content)
                    for i in partyRegs:
                        #gets information from the discord messages
                        pname = i.split("\n")[0].replace("#", "").strip()
                        #checks if data is in requests
                        if not pname in requests.keys():
                            requests[pname] = []
                        if pname == args[1]: #if party is correct party saves the owner and breaks the loop
                            pfounder = ctx.guild.get_member(int(i.split("\n")[2].replace("Party Founder/Leader:", "").strip().replace("<", "").replace(">", "").replace("@", "")))
                            break
                    requests[pname].append(ctx.author.id) #adds user to requests list, prevents them from spamming requests
                    #building the join request message
                    button = discord.ui.Button(label="Accept", style=discord.ButtonStyle.green)
                    button2 = discord.ui.Button(label="Deny", style=discord.ButtonStyle.red)
                    async def button_callback(interaction:discord.Interaction):
                        if not interaction.is_expired():
                            requests[pname].remove(ctx.author.id)
                            view.remove_item(button); view.remove_item(button2)
                            await ctx.author.send(f"> Your request to join {pname} has been accepted.")
                            v = False
                            for i in await ctx.guild.fetch_roles():
                                if i.name == args[1]:
                                    await ctx.author.add_roles(i, reason=f"Approved by {pfounder.name}")
                                    await interaction.message.edit(content="> Request has been sucessfully responded", view=view)
                                    v = True
                                    break
                            if v == False:
                                await interaction.message.edit(conten="> Role doesn't exist! Generate one with `/party genrole`.", view=view)
                        else:
                            await interaction.message.edit(content="> Request has timed out", view=view)
                    async def button2_callback(interaction:discord.Interaction):
                        if not interaction.is_expired():
                            requests[pname].remove(ctx.author.id)
                            await ctx.author.send(f"> Your request to join {pname} has been denied.")
                            view.remove_item(button); view.remove_item(button2)
                            await interaction.message.edit(content="> Request has been sucessfully responded", view=view)
                        else:
                            await interaction.message.edit(content="> Request has timed out", view=view)
                    button.callback = button_callback
                    button2.callback = button2_callback
                    view = discord.ui.View()
                    view.add_item(button); view.add_item(button2)
                    await ctx.reply("> Your request has been sent!")
                    await client.get_user(pfounder.id).send(f">>> {ctx.author.display_name} wants to join the {pname}", view = view)
            else:
                await ctx.reply("> Party doesn't have its joins open!")
        else:
            await ctx.reply("> Party doesn't exist!")
@client.command(name="?")
async def help(ctx:commands.Context):
    await ctx.reply("""## Commands\n- `/party`\n\t- `view` - 'Shows summary of all parties in the politcal parties channel'\n\t- `setdetails` `<partyname>` `<details>` - 'Allows the owner to set details regarding their party'\n\t- `details` `<partyname>` - 'Allows user to see a party's details\n\t- `join` `<partyname>` - 'Allows a user to request to join a party with its joins set to open'\n\t- `members` `<partyname>` - 'Allows a user to see a list of the members of a desired party'""")
with open('token.txt', 'r') as f:
    client.run(f.readlines()[0])
