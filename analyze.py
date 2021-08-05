import argparse
import csv
import os
import sys

import jieba
import pandas as pd


NUM_POSTS = 50


def parse_args():
    opts = argparse.ArgumentParser(description='Test users for inclusion.')
    opts.add_argument('posts_dir')
    opts.add_argument('keywords_file')
    opts.add_argument('-n', type=int, default=NUM_POSTS)
    return opts.parse_args()


def get_user_id(posts_user):
    data_files = os.listdir(posts_user)
    user_id = data_files[0].split('.')[0]
    return user_id


"""
@param posts_user: The path to a single user directory to process
"""
def load_posts(posts_user, n=NUM_POSTS):
    user_id = get_user_id(posts_user)
    posts_file = os.path.join(posts_user, '{}.csv'.format(user_id))
    posts = pd.read_csv(posts_file, nrows=n)
    #posts.loc[:, 'user_nickname'] = os.path.basename(posts_user.strip('/'))
    return user_id, posts


def load_keywords(keywords_file):
    keywords = []
    with open(keywords_file) as f:
        for keyword in f:
            keywords.append(keyword)
    return set(keywords)


def tokenize_posts(posts):
    posts.loc[:, 'weibo_text_tok'] = posts['weibo_text'].apply(lambda x: list(jieba.cut(x)))
    return posts


def check_for_keywords(posts, keywords):
    posts.loc[:, 'contains_keyword'] = posts['weibo_text_tok'].apply(lambda toks: len(keywords & set(toks)) > 0)
    return posts


def original_posts(posts):
    orig_posts = posts.loc[posts.if_it_is_original == True, :]
    return orig_posts


class UserStats(object):
    def __init__(self, user_id, posts, keywords):
        self.user_id = user_id
        self.posts = posts
        self.keywords = keywords

        # Calculated
        self.num_posts = self.posts.shape[0]

    def _matches_spam_keyword(self):
        self.posts = tokenize_posts(self.posts)
        self.posts = check_for_keywords(self.posts, self.keywords)

    def _num_orig_posts(self):
        self.orig_posts = original_posts(self.posts)
        num_orig = self.orig_posts.shape[0]
        return num_orig

    @property
    def valid_user(self):
        # First note whether each post matches a spam keyword
        self._matches_spam_keyword()

        # Get number of original posts
        self.num_orig = self._num_orig_posts()

        # Get number of original posts matching a spam keyword
        self.num_spam = self.orig_posts.loc[self.orig_posts.contains_keyword == True, :].shape[0]

        # Percent ads
        self.perc_spam = self.num_spam / self.num_orig
        valid_user = self.num_orig >= 25 and self.perc_spam >= 0.5

        return int(valid_user)


def main():
    args = parse_args()

    all_user_stats = []
    for user in os.listdir(args.posts_dir):
        user_dir = os.path.join(args.posts_dir, user)

        user_id, posts = load_posts(user_dir, n=args.n)
        keywords = load_keywords(args.keywords_file)

        user_stats = UserStats(user_id, posts, keywords)
        all_user_stats.append(user_stats)

    print(','.join(['user_id', 'valid_user', 'num_posts', 'num_orig_posts', 'num_spam', 'perc_spam']))
    stats_writer = csv.writer(sys.stdout)
    for user in all_user_stats:
        user_stats = (user.user_id, user.valid_user, user.num_posts, user.num_orig, user.num_spam, user.perc_spam)
        stats_writer.writerow(user_stats)


if __name__ == '__main__':
    main()
