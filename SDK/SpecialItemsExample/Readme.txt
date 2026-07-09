This is an example Quest to show how to use custom special items in a quest.

A custom item called "MagicBall" is defined in the SpecialItem_Descriptions.xml.  This quest initialization function creates a "MagicBall" inventory item in the Dark Castle.  The player must then find the Dark Castle and destroy it, causing the Dark Castle to drop the item.  While the item is dropped on the map, it can run scripts, just like any other agent and it does, spawning monsters near it as well as trying to find its owner.  The first drop of the item also spawns a boss monster who comes looking for the item.

A hero can pick up the item, and when it does, the custom item will attach a script to the new owner, so it can still do things.  This is needed because when an item is in the inventory of another agent, it is simply an ID in a list and no longer an agent of its own.

Once the item has been found, the goal of the quest is to kill the boss monster, Dorgo.  He will attempt to get the MagicBall back and if he comes near it, he will pick it up.  The MagicBall will give him healing powers while he has it in his possession.

