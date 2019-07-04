from django.db.models import Count, Q

from fbposts.constants import Reactions
from fbposts.models import Reaction, Post


def react_to_post(user_id, post_id, reaction_type):
    reactions_list = [Reactions.LIKE.value, Reactions.LOVE.value, Reactions.HAHA.value, Reactions.WOW.value,
                      Reactions.SAD.value, Reactions.ANGRY.value]
    if reaction_type not in reactions_list:
        return "enter appropriate reaction"

    try:
        user_reaction = Reaction.objects.get(post_id=post_id, reactor_id=user_id)
    except Reaction.DoesNotExist:
        Reaction.objects.create(reactor_id=user_id, post_id=post_id, reaction_type=reaction_type)
        return
    delete_or_update_user_reaction(user_reaction, reaction_type)


def react_to_comment(user_id, comment_id, reaction_type):
    reactions_list = [Reactions.LIKE.value, Reactions.LOVE.value, Reactions.HAHA.value, Reactions.WOW.value,
                      Reactions.SAD.value, Reactions.ANGRY.value]
    if reaction_type not in reactions_list:
        return "enter appropriate reaction"

    try:
        user_reaction = Reaction.objects.get(comment_id=comment_id, reactor_id=user_id)
    except Reaction.DoesNotExist:
        Reaction.objects.create(reactor_id=user_id, comment_id=comment_id, reaction_type=reaction_type)
        return
    delete_or_update_user_reaction(user_reaction, reaction_type)


def delete_or_update_user_reaction(user_reaction, reaction_type):
    if user_reaction.reaction_type == reaction_type:
        user_reaction.delete()
    else:
        user_reaction.update(reaction_type=reaction_type)


def get_post_reaction_details(post):
    count = 0
    reactions_list = []
    result = post.reactions.all().values('reaction_type').annotate(count=Count('post'))
    for res in result:
        reactions_list.append(res['reaction_type'])
        count = count + res['count']
    reactions = dict()
    reactions["count"] = count
    reactions["type"] = reactions_list
    return reactions


def get_comment_reaction_details(comment):
    total_count = 0
    reactions_list = []
    result = comment.reactions.all().values('reaction_type').annotate(count=Count('comment'))
    for res in result:
        reactions_list.append(res['reaction_type'])
        total_count = total_count + res['count']
    reactions = dict()
    reactions["count"] = total_count
    reactions["type"] = reactions_list
    return reactions


def get_reaction_metrics(post_id):
    return get_post_reaction_metrics(Post.objects.get(pk=post_id))


def get_total_reaction_count():
    reactions_dict = dict()
    result = Reaction.objects.values('post__id').filter(~(Q(post__id=None))).annotate(count=Count('reaction_type'))
    for post in result:
        reactions_dict[post['post__id']] = post['count']
    return reactions_dict


def get_post_reaction_metrics(post):
    reactions_dict = dict()
    result = post.reactions.all().values('reaction_type').annotate(count=Count('post'))
    for res in result:
        reactions_dict[res['reaction_type']] = res['count']
    return reactions_dict

