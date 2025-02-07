from fbposts.models import Comment
from fbposts.reactions import get_all_comments_reaction_details
from fbposts.views import get_user_to_dict


def add_comment(post_id, comment_user_id, comment_text):
    if comment_text == "":
        raise (ValueError)
    comment = Comment.objects.create(post_id=post_id, commenter_id=comment_user_id, comment_content=comment_text)
    return comment.id


def reply_to_comment(comment_id, reply_user_id, reply_text):
    if reply_text == "":
        raise (ValueError)
    parent_comment = Comment.objects.select_related('comment').get(pk=comment_id)
    new_comment = Comment()
    if parent_comment.post is None:
        new_comment.comment = parent_comment.comment
    else:
        new_comment.comment = parent_comment
    new_comment.commenter_id = reply_user_id
    new_comment.comment_content = reply_text
    new_comment.save()
    return new_comment.id


def get_replies_for_comment(comment_id):
    comment = Comment.objects.all().filter(pk=comment_id).prefetch_related('reactions', 'replies', 'replies__reactions',

                                                                           'commenter', 'replies__commenter')
    replies = comment[0].replies.all()
    replies_ids = []
    for reply in replies:
        replies_ids.append(reply.id)
    comment_reactions = get_all_comments_reaction_details(replies_ids)
    replies = get_comments(comment[0].replies.all(), comment_reactions)

    for r in replies:
        del r["reactions"]

    return replies


def get_comments(comments, reactions):
    list_of_comments = []

    for comment in comments:

        comment_dict = dict()

        comment_dict["comment_id"] = comment.id
        comment_dict["commenter"] = get_user_to_dict(comment.commenter)
        comment_dict["commented_at"] = comment.commented_at.strftime("%y-%m-%d %H:%M:%S.%f")

        comment_dict["comment_content"] = comment.comment_content
        comment_dict["reactions"] = reactions[comment.id]
        if comment.post is not None:
            replies = get_comments(comment.replies.all(), reactions)
            comment_dict["replies_count"] = len(replies)
            comment_dict["replies"] = replies
        list_of_comments.append(comment_dict)

    return list_of_comments
