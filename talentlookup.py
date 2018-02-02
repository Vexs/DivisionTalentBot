import discord
from discord.ext import commands
import json
import re

class TalentLookup:
    """"""
    def __init__(self, bot):
        self.bot = bot
        with open("talents.json", "r") as f:
            self.talent_dict = json.load(f)
        with open("gearsets.json", "r") as f:
            self.gearset_dict = json.load(f)
        self.emoji_dict = {"Shotgun": "<:shotgun:408739032579964928>",
                           "MMR": "<:MMR:408739032562925568>",
                           "Pistol": "<:pistol:408739032563056640>",
                           "LMG": "<:lmg:408739032135106572>",
                           "AR": "<:ar:408739032474845184>",
                           "SMG": "<:smg:408739032244158466>"}
        # I'm too lazy to edit the whole json again so this
        for value in self.talent_dict.values():
            value[1] = value[1].replace(",",'')
            for k, v in self.emoji_dict.items():
                value[1] = value[1].replace(k, v)

    @commands.command()
    async def talent(self, *,args):
        """Looks up a talent!"""
        args = args.split(';')
        is_first = True
        embed = discord.Embed()
        embed.color = discord.Color(value=0xFF6D10)
        for index, arg in enumerate(args[:3]):
            arg = arg.lower()
            arg = arg.strip()
            talent = self.talent_dict.get(arg.lower())

            if not talent:
                possibles = finder(arg, self.talent_dict.keys(), lazy=False)
                if len(possibles) == 1:
                    talent = self.talent_dict.get(possibles[0])
                    arg = possibles[0]
                elif possibles and is_first:
                    possibles = [x.title() for x in possibles]
                    await self.bot.say("Did you mean...\n{}".format("\n".join(possibles[:5])))
                    return
                elif is_first:
                    await self.bot.say("No results found!")
                    return
                else:
                    continue
            formatted_output = "{0}\n\n**Avaliable on/as:**\n{1}".format(*talent)
            try:
                args[index+1] # add a line between fields for readability
                formatted_output += "\n-----------------------------------------"
            except:
                pass

            if is_first:
                is_first = False
                embed.set_author(name=arg.title())
                embed.description = formatted_output
                try:
                    embed.set_thumbnail(url=talent[2])
                except IndexError:
                    pass
                except Exception as e:
                    print(e)
            else:
                embed.add_field(name=arg.title(), value=formatted_output)

        await self.bot.say(embed=embed)

    @talent.error
    async def _talent_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            pass
        else:
            print(error)

    @commands.command()
    async def talentsearch(self, *args):
        """Searches talents by what they do"""
        args = [x.lower() for x in args]
        results = []
        for key, value in self.talent_dict.items():
            if any(arg in key for arg in args):
                results.append(key.title())
                continue
            for subvalue in value:
                if all(arg in subvalue for arg in args):
                    results.append(key.title())
        if results:
            await self.bot.say("Found the following talents: \n{}".format("\n".join(results[:10])))
        else:
            await self.bot.say("Found no talents")

    @commands.command()
    async def gearset(self, *, arg):
        """Looks up a gearset"""
        arg = arg.lower()
        gearset = self.gearset_dict.get(arg)
        if not gearset:
            possibles = finder(arg, self.gearset_dict.keys(), lazy=False)
            if len(possibles) == 1:
                gearset = self.gearset_dict.get(possibles[0])
                arg = possibles[0]
            elif possibles:
                possibles = [x.title() for x in possibles]
                await self.bot.say("Did you mean...\n{}".format("\n".join(possibles[:3])))
                return
            else:
                await self.bot.say("No results found!")
                return
        embed = discord.Embed()
        embed.color = discord.Color(value=0x18c773)
        output = ["**{}:**\n".format(arg.title())]
        embed.set_thumbnail(url=gearset[5])
        for index, value in enumerate(gearset[:5]):
            output.append("**{}:** {}\n".format(index+2, value))

        embed.description = "".join(output)

        await self.bot.say(embed=embed)




def setup(bot):
    bot.add_cog(TalentLookup(bot))


def finder(text, collection, *, key=None, lazy=True):
    #Thanks to Rapptz
    suggestions = []
    text = str(text)
    pat = '.*?'.join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)
    for item in collection:
        to_search = key(item) if key else item
        r = regex.search(to_search)
        if r:
            suggestions.append((len(r.group()), r.start(), item))

    def sort_key(tup):
        if key:
            return tup[0], tup[1], key(tup[2])
        return tup

    if lazy:
        return (z for _, _, z in sorted(suggestions, key=sort_key))
    else:
        return [z for _, _, z in sorted(suggestions, key=sort_key)]
