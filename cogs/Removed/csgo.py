import requests
import bs4

base_url = "https://steamcommunity.com/market/search?q="
csgo = "&appid=730"
q_any = "any"

price_ascending = "#p1_price_asc"
price_descending = "#p1_price_desc"

wear = "&category_730_Exterior%5B0%5D="
wear_factory_new = "tag_WearCategory0"
wear_minimal_wear = "tag_WearCategory1"
wear_field_tested = "tag_WearCategory2"
wear_well_worn = "tag_WearCategory3"
wear_battle_scarred = "tag_WearCategory4"
wear_na = "tag_WearCategoryNA"  # default knives skins

quality = "&category_730_Quality%5B%5D="
quality_normal = "tag_normal"
quality_stattrak = "tag_strange"
quality_souvenir = "tag_tournament"
quality_star = "tag_unusual"
quality_star_stattrak = "tag_unusual_strange"

rarity = "&category_730_Rarity%5B%5D="
rarity_consumer = "tag_Rarity_Common_Weapon"
rarity_mil_spec = "tag_Rarity_Rare_Weapon"
rarity_industrial = "tag_Rarity_Uncommon_Weapon"
rarity_restricted = "tag_Rarity_Mythical_Weapon"
rarity_classified = "tag_Rarity_Legendary_Weapon"
rarity_covert = "tag_Rarity_Ancient_Weapon"
rarity_base_grade = "tag_Rarity_Common"
rarity_extraordinary = "tag_Rarity_Ancient"
rarity_high_grade = "tag_Rarity_Rare"
rarity_exotic = "tag_Rarity_Legendary"
rarity_remarkable = "tag_Rarity_Mythical"
rarity_contraband = "tag_Rarity_Contraband"

weapon = "&category_730_Weapon%5B%5D="

weapon_ak_alias = ["AK-47", "tag_weapon_ak47",
                   "ak", "ak47", "ak-47"]

weapon_aug_alias = ["AUG", "tag_weapon_aug",
                    "aug"]

weapon_awp_alias = ["AWP", "tag_weapon_awp",
                    "awp", "avp", "magnum", "asiimov", "asimov"]

weapon_bayonet_alias = ["Bayonet (Knife)", "tag_weapon_bayonet",
                        "bayonet"]

weapon_bowie_alias = ["Bowie (Knife)", "tag_weapon_knife_survival_bowie"
                      "bowie"]

weapon_butterfly_alias = ["Butterfly (Knife)", "tag_weapon_butterfly",
                          "butterfly"]

weapon_cz_alias = ["CZ75", "tag_weapon_cz75a"
                   "cz", "cz75", "cz75a", "look at me i think im a csgo pro"]

weapon_deagle_alias = ["Desert Eagle", "tag_weapon_deagle"
                       "deag", "deagle", "juan", "desert", "eagle"]

weapon_dual_berettas_alias = ["Dual Beretta's", "tag_weapon_elite",
                              "beretta's", "berretta", "dual b's", "dualies", "dual", "dual bs", "dual b",
                              "it's high noon"]

weapon_falchion_alias = ["Falchion (Knife)", "tag_weapon_knife_falchion",
                         "falchion"]

weapon_famas_alias = ["FAMAS", "tag_weapon_famas",
                      "famas"]

weapon_five_seven_alias = ["Five-SeveN", "tag_weapon_fiveseven",
                           "5-7", "five", "seven", "five-seven", "five seven"]

weapon_flipknife_alias = ["Flip Knife", "tag_weapon_knife_flip",
                          "flip", "flipknife", "flip knife"]

weapon_t_auto_alias = ["G3SG1", "tag_weapon_g3sg1",
                       "t auto", "t auto sniper", "g3sg1"]

weapon_galil_alias = ["Galil", "tag_weapon_galilar",
                      "galil"]

weapon_glock_alias = ["Glock-18", "tag_weapon_glock",
                      "glock", "t pistol", "glock 18", "glock-18", "g18"]

weapon_gutknife_alias = ["Gut Knife", "tag_weapon_knife_gut",
                         "gut knife", "gutknife", "gut"]

weapon_huntsman_alias = ["Huntsman (Knife)", "tag_weapon_knife_tactical",
                         "huntsman", "tactical"]

weapon_karambit_alias = ["Karambit (Knife)", "tag_weapon_knife_karambit",
                         "karambit"]

weapon_m249_alias = ["M249", "tag_weapon_m249",
                     "m249"]

weapon_m4a1s_alias = ["M4A1-S", "tag_weapon_m4a1_silencer",
                      "m4a1s", "m4a1-s"]

weapon_m4a4_alias = ["M4A4", "tag_weapon_m4a1",
                     "m4a4", "m4"]

weapon_m9_bayonet_alias = ["M9 Bayonet", "tag_weapon_knife_m9_bayonet",
                           "m9", "m9 bayonet"]

weapon_mac10_alias = ["MAC-10", "tag_weapon_mac10",
                      "mac10", "mac 10", "mac", "mac-10"]

weapon_mag7_alias = ["MAG-7", "tag_weapon_mag7",
                     "mag7", "mag-7", "mag 7"]

weapon_mp7_alias = ["MP7", "tag_weapon_mp7",
                    "mp7", "mp 7"]

weapon_mp9_alias = ["MP9", "tag_weapon_mp9",
                    "mp9", "mp 9"]

weapon_negev_alias = ["Negev", "tag_weapon_negev",
                      "negev", "suppressing fire"]

weapon_nova_alias = ["Nova", "tag_weapon_nova",
                     "nova", "quebec's"]

weapon_p2000_alias = ["P2000", "tag_weapon_hkp2000",
                      "p2000", "ct pistol"]

weapon_p250_alias = ["P250", "tag_weapon_p250",
                     "p250"]

weapon_p90_alias = ["P90", "tag_weapon_p90",
                    "p90", "spray and pray", "rush b"]

weapon_bizon_alias = ["PP-Bizon", "tag_weapon_bizon",
                      "pp bizon", "pp-bizon", "bizon", "don't bizon"]

weapon_r8_revolver_alias = ["R9 Revolver", "tag_weapon_revolver",
                            "r8", "r8 revolver", "r8-revolver", "revolver"]

weapon_sawedoff_alias = ["Sawed-Off", "tag_weapon_sawedoff",
                         "sawed off", "sawed", "sawed-off", "sawedoff"]

weapon_ct_auto_alias = ["SCAR-20", "tag_weapon_scar20",
                        "ct auto", "scar 20", "scar20", "scar-20", "scar"]

weapon_sg_553_alias = ["SG 553", "tag_weapon_sg556",
                       "sg-553", "sg 553", "sg553"]

weapon_shadow_daggers_alias = ["Shadow Daggers", "tag_weapon_knife_push",
                               "shadow", "daggers", "shadow daggers", "shadow daggers", "butt plugs", "plugs"]

weapon_scout_alias = ["SSG 08 (Scout)", "tag_weapon_ssg08",
                      "ssg08", "scout", "ssg", "ssg-08", "ssg 08", "ssg 8", "ssg8", "ssg-8"]

weapon_tec9_alias = ["Tec-9", "tag_weapon_tec9",
                     "tec9", "rek9", "tec-9", "tec 9"]

weapon_ump45_alias = ["UMP-45", "tag_weapon_ump45",
                      "ump", "ump45", "ump-45", "ump 45"]

weapon_usp_alias = ["USP-S", "tag_weapon_usp_silencer",
                    "usp", "usp-s", "usp s", "usps", "one tap", "scream", "they talk about my one taps"]

weapon_xm1014_alias = ["XM1014", "tag_weapon_xm1014",
                       "auto shotgun", "auto shotty", "auto shotty", "xm1014"]

all_aliases = [weapon_ak_alias, weapon_aug_alias, weapon_awp_alias, weapon_bayonet_alias, weapon_bowie_alias,
               weapon_butterfly_alias, weapon_cz_alias, weapon_deagle_alias, weapon_dual_berettas_alias,
               weapon_falchion_alias, weapon_famas_alias, weapon_five_seven_alias, weapon_flipknife_alias,
               weapon_t_auto_alias, weapon_galil_alias, weapon_glock_alias, weapon_gutknife_alias,
               weapon_huntsman_alias, weapon_karambit_alias, weapon_m249_alias, weapon_m4a1s_alias,
               weapon_m4a4_alias, weapon_m9_bayonet_alias, weapon_mac10_alias, weapon_mag7_alias,
               weapon_mp7_alias, weapon_mp9_alias, weapon_negev_alias, weapon_nova_alias, weapon_p2000_alias,
               weapon_p250_alias, weapon_p90_alias, weapon_bizon_alias, weapon_r8_revolver_alias,
               weapon_sawedoff_alias, weapon_ct_auto_alias, weapon_sg_553_alias, weapon_shadow_daggers_alias,
               weapon_scout_alias, weapon_tec9_alias, weapon_ump45_alias, weapon_usp_alias, weapon_xm1014_alias]

"""
@commands.command(name="csgo", pass_context=True)
async def csgo_command(self, ctx):
    ""Start a CSGO Market Search""
    timeout_msg = "No reply within 60 seconds. Cancelling search"

    search_gun = None
    search_skin = None

    tag_gun = None
    tag_skin = None

    # First get Weapon Name
    await self.bot.say("{} please enter the name of the Weapon you'd like to search for."
                       "".format(ctx.message.author.mention))
    w_gun_msg = await self.bot.wait_for_message(author=ctx.message.author,
                                                channel=ctx.message.channel,
                                                timeout=60)
    if w_gun_msg is None:
        await self.bot.say(timeout_msg)
        return

    wgm_content = w_gun_msg.content

    for aliases in csgo.all_aliases:
        for alias in aliases:
            if alias in str(wgm_content).lower():
                search_gun = aliases[0]
                tag_gun = aliases[1]
                break

    await self.bot.say("{} please enter the name of the '{}' skin you would like to find. Or type '//' to only"
                       "search by weapon."
                       "".format(ctx.message.author.mention, search_gun))

    w_skin_msg = await self.bot.wait_for_message(author=ctx.message.author,
                                                 channel=ctx.message.channel,
                                                 timeout=60)

    if w_skin_msg is None:
        await self.bot.say(timeout_msg)
        return

    wsm_content = w_skin_msg.content

    sorting_prefix = None

    if wsm_content == "//" or wsm_content == "'//'":
        sorting_prefix = "Won't search with a skin name"
    else:
        sorting_prefix = "Will search with skin name '{}'".format(search_skin)

    ""
    sorting_react = await self.bot.say("{}. {}.\n"
                                       "\n"
                                       "How "
                                       "")
    ""

    if tag_skin is None:
        url = csgo.base_url + csgo.weapon + tag_gun
    else:
        url = csgo.base_url + tag_skin + csgo.weapon + tag_gun

    search_data = requests.get(url)
"""
"""
p1_name_asc
p1_name_desc

p1_quantity_asc
p1_quantity_desc

p1_price_asc
p1_price_desc

p1_popular_asc - same results as p1_popular_desc
p1_popular_desc
"""


"""
@commands.command(pass_context=True)
async def csgo(self, ctx):
    ""Type 'csgo' to start a weapon skin search""

    timeout_msg = "No reply within 60 seconds. Cancelling command"

    search_gun = None
    search_rarity = None
    search_quality = None
    search_wear = None
    search_name = None

    tag_gun = None
    tag_rarity = None
    tag_quality = None
    tag_wear = None
    tag_name = None

    # can_search = False
    keep_looped = True

    while keep_looped is True:

        if search_gun is None:
            msg_gun_name = "Type 1 for Gun Name"
        else:
            msg_gun_name = "Type 1 for Gun Name - Currently set to '{}'".format(search_gun)

        if search_rarity is None:
            msg_rarity = "Type 2 for Rarity"
        else:
            msg_rarity = "Type 2 for Rarity - Currently set to '{}'".format(search_rarity)

        if search_quality is None:
            msg_quality = "Type 3 for Quality"
        else:
            msg_quality = "Type 3 for Quality - Currently set to '{}'".format(search_quality)

        if search_wear is None:
            msg_wear = "Type 4 for Wear"
        else:
            msg_wear = "Type 4 for Wear - Currently set to '{}'".format(search_wear)

        if search_name is None:
            msg_skin_name = "Type 5 for Skin Name"
        else:
            msg_skin_name = "Type 5 for Skin Name - Currently set to '{}'".format(search_name)

        if search_name is not None or search_wear is not None \
                or search_quality is not None or search_rarity is not None or search_gun is not None:
            can_search = True
        else:
            can_search = False

        if can_search is False:
            msg_searchable = "At least one item needs to be set before a search can be performed"
        else:
            msg_searchable = "Type 'done' once you are done"

        t_msg = await self.bot.say("Search options\n"
                                   "{}\n"
                                   "{}\n"
                                   "{}\n"
                                   "{}\n"
                                   "{}\n"
                                   "\n"
                                   "{}".format(msg_gun_name, msg_rarity, msg_quality, msg_wear,
                                               msg_skin_name, msg_searchable))

        w_msg = await self.bot.wait_for_message(author=ctx.message.author,
                                                channel=ctx.message.channel,
                                                timeout=60)

        await self.bot.delete_message(t_msg)

        if w_msg is not None:
            await self.bot.delete_message(w_msg)
            msg_c = w_msg.content

            if msg_c == "1" or msg_c == "'1'":
                await self.bot.say("Please type the name of the gun you would like to search using")
                gun_reply = await self.bot.wait_for_message(author=ctx.message.author,
                                                            channel=ctx.message.channel,
                                                            timeout=60)
                if gun_reply is None:
                    await self.bot.say(timeout_msg)
                    return

                gr_msg = gun_reply.content

                await self.bot.delete_message(gun_reply)

                for aliases in csgo.all_aliases:
                    for alias in aliases:
                        if alias in str(gr_msg).lower():
                            search_gun = aliases[0]
                            tag_gun = aliases[1]
                            break

            elif msg_c == "2" or msg_c == "'2'":
                await self.bot.say("rarity")

            elif msg_c == "3" or msg_c == "'3'":
                await self.bot.say("quality")

            elif msg_c == "4" or msg_c == "'4'":
                await self.bot.say("wear")

            elif msg_c == "5" or msg_c == "'5'":
                s_msg = await self.bot.say("Please type the name of the skin (or partial name) you would like"
                                           "to search for")
                skin_reply = await self.bot.wait_for_message(author=ctx.message.author,
                                                             channel=ctx.message.channel,
                                                             timeout=60)
                await self.bot.delete_message(s_msg)

                if skin_reply is None:
                    await self.bot.say(timeout_msg)
                    return

                skin = str(skin_reply.content).replace(" ", "+")

                search_name = skin
                tag_name = skin

            elif msg_c == "done" or msg_c == "'done'":
                if can_search is True:
                    full_url = csgo.base_url
                    if search_name is not None:
                        full_url += tag_name
                    if search_gun is not None:
                        full_url += "{}{}".format(csgo.weapon, tag_gun)
                    if search_rarity is not None:
                        full_url += "{}{}".format(csgo.rarity, tag_rarity)
                    if search_quality is not None:
                        full_url += "{}{}".format(csgo.quality, tag_quality)
                    if search_wear is not None:
                        full_url += "{}{}".format(csgo.wear, tag_wear)

                    print(full_url)
                    await self.bot.say("this is where the search would be done")
                    return

        else:
            await self.bot.say(timeout_msg)
            print("not as nice")
            keep_looped = False
            return





    @commands.command(name="csgo", pass_context=True)
    async def csgo_command(self, ctx):
        term = simplify.remove_prefix_in_message(self.bot, ctx.message, "csgo")
        manual_search = False

        url_base = csgo.base_url
        final_url = None

        if term is None:
            manual_search = True

        if manual_search is False:
            final_url = url_base + term + csgo.csgo
        else:
            print("boring stuff")

        if final_url is None:
            print("error or something")
        else:"""