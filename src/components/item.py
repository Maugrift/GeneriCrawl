from random import randint

import libtcodpy as libtcod
from game_messages import Message
from status_effect import StatusEffect


def get_throw_target(game_map, **kwargs):
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    entities = game_map.get_entities_at_tile(target_x, target_y, blocking_only=True)
    throw_target = None
    for entity in entities:
        if entity.fighter:
            throw_target = entity

    return throw_target


def equip(*args, **kwargs):
    user = args[0]
    item = args[1]

    results = user.slots.toggle_equip(item)
    equipped = results.get('equipped')
    unequipped = results.get('unequipped')

    if equipped and unequipped:
        results['use_message'] = Message('You swap out {0} for {1}.'.format(unequipped.definite_name,
                                                                            equipped.definite_name), libtcod.light_blue)
    elif equipped:
        results['use_message'] = Message('You equip {0}.'.format(equipped.definite_name), libtcod.light_blue)
    elif unequipped:
        results['use_message'] = Message('You unequip {0}.'.format(unequipped.definite_name), libtcod.light_blue)

    user.fighter.hp = min(user.fighter.hp, user.fighter.max_hp)

    return results


def throw_std(*args, **kwargs):
    item = args[1]
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    target = get_throw_target(args[2], **kwargs)

    results = {'item_moved': item, 'item_x': target_x, 'item_y': target_y}

    if not target:
        return results

    amount = kwargs.get('amount')
    if not amount and item.equipment:
        amount = item.equipment.attack_bonus

    if not amount:
        amount = randint(1, 4)

    results.update(target.fighter.take_damage(amount))
    if amount > 0:
        results['use_message'] = Message('{0} hits {1} for {2} HP.'.format(item.definite_name.capitalize(),
                                                                           target.definite_name, amount))
    else:
        results['use_message'] = Message('{0} bounces off {1} harmlessly.'.format(item.definite_name.capitalize(),
                                                                                  target.definite_name))
    return results


def heal(*args, **kwargs):
    item = args[1]
    amount = kwargs.get('amount')
    throwing = kwargs.get('throwing')

    if not throwing:
        target = args[0]
    else:
        target = get_throw_target(args[2], **kwargs)
        if not target:
            target_x = kwargs.get('target_x')
            target_y = kwargs.get('target_y')
            return {'item_moved': item, 'item_x': target_x, 'item_y': target_y}

    results = {}

    player_using = target == args[0]

    if target.fighter.hp == target.fighter.max_hp:
        if player_using:
            results['use_message'] = Message('You are already fully healed.', libtcod.yellow)
        else:
            results['item_consumed'] = item
            results['use_message'] = Message('The rune has no effect on {0}.'.format(target.definite_name),
                                             libtcod.yellow)
    else:
        if type(amount) is float:
            actual_amount = int(target.fighter.max_hp * amount)
        else:
            actual_amount = amount

        amount_healed = target.fighter.heal(actual_amount)
        results['item_consumed'] = item
        if player_using:
            results['use_message'] = Message('You feel rejuvenated! You recover {0} HP.'.format(amount_healed),
                                             libtcod.green)
        else:
            results['use_message'] = Message('{0} recovers {1} HP.'.format(target.definite_name.capitalize(),
                                                                           amount_healed),
                                             libtcod.green)

    return results


def pain(*args, **kwargs):
    item = args[1]
    amount = kwargs.get('amount')
    throwing = kwargs.get('throwing')

    if not throwing:
        target = args[0]
    else:
        target = get_throw_target(args[2], **kwargs)
        if not target:
            target_x = kwargs.get('target_x')
            target_y = kwargs.get('target_y')
            return {'item_moved': item, 'item_x': target_x, 'item_y': target_y}

    player_using = target == args[0]

    if type(amount) is float:
        actual_amount = int(target.fighter.max_hp * amount)
    else:
        actual_amount = amount

    results = target.fighter.take_damage(actual_amount)
    results['item_consumed'] = item
    if player_using:
        results['use_message'] = Message('You feel a searing pain! You lose {0} HP.'.format(actual_amount),
                                         libtcod.red)
    else:
        results['use_message'] = Message('{0} loses {1} HP.'.format(target.definite_name.capitalize(), actual_amount),
                                         libtcod.red)

    return results


def might(*args, **kwargs):
    item = args[1]
    amount = kwargs.get('amount')
    duration = kwargs.get('duration')
    throwing = kwargs.get('throwing')

    if not throwing:
        target = args[0]
    else:
        target = get_throw_target(args[2], **kwargs)
        if not target:
            target_x = kwargs.get('target_x')
            target_y = kwargs.get('target_y')
            return {'item_moved': item, 'item_x': target_x, 'item_y': target_y}

    player_using = target == args[0]

    if type(amount) is float:
        actual_amount = int(target.fighter.attack * amount)
    else:
        actual_amount = amount

    total_amount = actual_amount
    existing_effect = target.get_status_effect('strengthened')
    if existing_effect:
        total_amount += existing_effect.properties.get('attack_bonus')
        duration += target.status_effects.get(existing_effect)
        target.status_effects.pop(existing_effect)

    target.status_effects.update({StatusEffect('strengthened', {'attack_bonus': total_amount}, None): duration})

    results = {'item_consumed': item}
    if player_using:
        results['use_message'] = Message('Your muscles grow rapidly! You gain {0} attack.'.format(actual_amount),
                                         libtcod.yellow)
    else:
        results['use_message'] = Message('{0} appears stronger.'.format(target.definite_name.capitalize()),
                                         libtcod.yellow)

    return results


def protection(*args, **kwargs):
    item = args[1]
    amount = kwargs.get('amount')
    duration = kwargs.get('duration')
    throwing = kwargs.get('throwing')

    if not throwing:
        target = args[0]
    else:
        target = get_throw_target(args[2], **kwargs)
        if not target:
            target_x = kwargs.get('target_x')
            target_y = kwargs.get('target_y')
            return {'item_moved': item, 'item_x': target_x, 'item_y': target_y}

    player_using = target == args[0]

    if type(amount) is float:
        actual_amount = int(target.fighter.defense * amount)
    else:
        actual_amount = amount

    total_amount = actual_amount
    existing_effect = target.get_status_effect('protected')
    if existing_effect:
        total_amount += existing_effect.properties.get('defense_bonus')
        duration += target.status_effects.get(existing_effect)
        target.status_effects.pop(existing_effect)

    target.status_effects.update({StatusEffect('protected', {'defense_bonus': total_amount}, None): duration})

    results = {'item_consumed': item}
    if player_using:
        results['use_message'] = Message('Your body feels tougher! You gain {0} defense.'.format(actual_amount),
                                         libtcod.yellow)
    else:
        results['use_message'] = Message('{0} appears more resilient.'.format(target.definite_name.capitalize()),
                                         libtcod.yellow)

    return results


def teleportation(*args, **kwargs):
    item = args[1]
    game_map = args[2]
    throwing = kwargs.get('throwing')

    if not throwing:
        target = args[0]
    else:
        target = get_throw_target(game_map, **kwargs)
        if not target:
            target_x = kwargs.get('target_x')
            target_y = kwargs.get('target_y')
            return {'item_moved': item, 'item_x': target_x, 'item_y': target_y}

    player_using = target == args[0]

    target.x, target.y = game_map.find_open_tile()

    results = {'item_consumed': item}
    if player_using:
        results['use_message'] = Message('Space warps around you and your surroundings suddenly change.',
                                         libtcod.magenta)
        results['recompute_fov'] = True
    else:
        results['use_message'] = Message('{0} suddenly vanishes.'.format(target.definite_name.capitalize()),
                                         libtcod.yellow)

    return results


class Item:
    def __init__(self, use_function=None, throw_function=throw_std, **kwargs):
        self.use_function = use_function
        self.throw_function = throw_function
        self.function_kwargs = kwargs

    def use(self, user, game_map, **kwargs):
        results = {}

        if kwargs.get('throwing'):
            kwargs.update(self.function_kwargs)
            throw_results = self.throw_function(user, self.owner, game_map, **kwargs)
            results.update(throw_results)
        elif self.use_function is None:
            results['use_message'] = Message('{0} cannot be used'.format(self.owner.definite_name.capitalize()),
                                             libtcod.yellow)
            return results
        else:
            kwargs.update(self.function_kwargs)
            item_use_results = self.use_function(user, self.owner, game_map, **kwargs)
            results.update(item_use_results)

        return results
