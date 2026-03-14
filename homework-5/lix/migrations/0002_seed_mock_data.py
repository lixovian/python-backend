from django.db import migrations


def seed_mock_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Post = apps.get_model('lix', 'Post')
    Comment = apps.get_model('lix', 'Comment')
    PostLike = apps.get_model('lix', 'PostLike')
    CommentLike = apps.get_model('lix', 'CommentLike')

    user1, _ = User.objects.get_or_create(
        username='alice',
        defaults={'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Smith'},
    )
    user1.set_password('alicepass123')
    user1.save(update_fields=['password'])

    user2, _ = User.objects.get_or_create(
        username='bob',
        defaults={'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Jones'},
    )
    user2.set_password('bobpass123')
    user2.save(update_fields=['password'])

    user3, _ = User.objects.get_or_create(
        username='carol',
        defaults={'email': 'carol@example.com', 'first_name': 'Carol', 'last_name': 'Brown'},
    )
    user3.set_password('carolpass123')
    user3.save(update_fields=['password'])

    post1, _ = Post.objects.get_or_create(
        author=user1,
        title='Welcome to the comments service',
        defaults={'content': 'This is the first test post'},
    )
    post2, _ = Post.objects.get_or_create(
        author=user2,
        title='Sample',
        defaults={'content': 'Mock-2'},
    )

    comment1, _ = Comment.objects.get_or_create(
        post=post1,
        author=user2,
        content='Positive comment',
    )
    comment2, _ = Comment.objects.get_or_create(
        post=post1,
        author=user3,
        content='Neutral comment',
    )
    comment3, _ = Comment.objects.get_or_create(
        post=post2,
        author=user1,
        content='Dislike comment',
    )

    PostLike.objects.get_or_create(post=post1, user=user2)
    PostLike.objects.get_or_create(post=post1, user=user3)
    PostLike.objects.get_or_create(post=post2, user=user1)

    CommentLike.objects.get_or_create(comment=comment1, user=user1)
    CommentLike.objects.get_or_create(comment=comment2, user=user1)
    CommentLike.objects.get_or_create(comment=comment3, user=user2)


def unseed_mock_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Post = apps.get_model('lix', 'Post')
    Comment = apps.get_model('lix', 'Comment')
    PostLike = apps.get_model('lix', 'PostLike')
    CommentLike = apps.get_model('lix', 'CommentLike')

    CommentLike.objects.all().delete()
    PostLike.objects.all().delete()
    Comment.objects.all().delete()
    Post.objects.all().delete()
    User.objects.filter(username__in=['alice', 'bob', 'carol']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('lix', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_mock_data, unseed_mock_data),
    ]

