import os
import imaplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone


def extract_email_category(email: str):
    """
    Extracts the category of the email.
    :param email: email to extract category from.
    :return: category of the email.
    """

    ttl_idx0 = email.find('Subject: ')
    if ttl_idx0 == -1:
        return None
    ttl_idx1 = email.find(' daily', ttl_idx0 + 1)
    ttl = email[ttl_idx0 + 9:ttl_idx1]
    return ttl


def reformat_email(msg: str, ttl: str, mark_authors=None, mark_titles=None, skip_words=None, send_marked_only=False) -> tuple:
    """
    Parses the email message and generates an improved (clean) version.
    :param msg: original email message.
    :param ttl: category of the email.
    :param mark_authors: list of authors to highlight.
    :param mark_titles: list of words in titles to highlight.
    :param skip_words: list of words to skip listings that feature them in their titles.
    :return: tuple of: (clean_email: str - html formatted email,
                        marked: bool, if the email contains a marked author to use with "advertise_marked").
    """

    if skip_words is None:
        skip_words = []
    if mark_titles is None:
        mark_titles = []
    if mark_authors is None:
        mark_authors = []

    links = []
    titles = []
    authors = []
    crossref = []
    replaced = []
    skipped = []
    skipped_num = [0] * len(skip_words)
    marked = []
    marked_num = [False] * len(mark_authors)
    keywords = []
    keywords_num = [False] * len(mark_titles)
    marked_firsts = [author.split(' ')[0] for author in mark_authors]
    marked_lasts = [author.split(' ')[-1] for author in mark_authors]

    listing_idx = [i for i in range(len(msg)) if msg.find('arXiv:', i) == i]
    listing_idx.append(len(msg))

    # loop over all the listings in the email:
    for idx in range(len(listing_idx) - 1):
        if idx >= len(listing_idx) - 1:  # in case we removed some items
            break
        cur_link = msg[listing_idx[idx] + 6:listing_idx[idx] + 16].replace('\r', '')
        while not 'https://arxiv.org/abs/' + cur_link in msg[listing_idx[idx] + 16:listing_idx[idx + 1]]:
            listing_idx.pop(idx + 1)
        cur_listing = msg[listing_idx[idx]:listing_idx[idx + 1]]  # .replace('\r\n', '')

        title_idx = cur_listing.find('Title: ')
        author_idx = cur_listing.find('Authors: ', title_idx)
        cat_idx = cur_listing.find('Categories: ', author_idx)
        cur_title = cur_listing[title_idx + 7:author_idx]
        cur_authors = cur_listing[author_idx + 9:cat_idx]

        # check if we should highlight one of the authors:
        marked.append(False)
        for i in range(len(mark_authors)):
            if marked_lasts[i].lower() in cur_authors.lower():
                cur_first = cur_authors.split(marked_lasts[i])[0].split(', ')[-1].split(' ')[0].lower()
                if cur_first == marked_firsts[i].lower() or cur_first == marked_firsts[i][0].lower() + '.':
                    marked[-1] = True
                    marked_num[i] = True

                    author_idx1 = cur_authors.lower().find(marked_lasts[i].lower()) + len(marked_lasts[i])
                    author_idx0 = cur_authors.lower().rfind(', ', 0, author_idx1)
                    author_idx0 = author_idx0 + 2 if author_idx0 >= 0 else 0

                    cur_authors = '{0}<b>{1}</b>{2}'.format(cur_authors[:author_idx0],
                                                            cur_authors[author_idx0:author_idx1],
                                                            cur_authors[author_idx1:])

        # check if we should highlight one of the keywords in the title:
        keywords.append(False)
        for i in range(len(mark_titles)):
            if mark_titles[i].lower() in cur_title.lower():
                keywords[-1] = True
                keywords_num[i] = True

                emph_idx0 = cur_title.lower().find(mark_titles[i].lower())
                emph_idx1 = emph_idx0 + len(mark_titles[i])

                cur_title = '{0}<b>{1}</b>{2}'.format(cur_title[:emph_idx0], cur_title[emph_idx0:emph_idx1],
                                                      cur_title[emph_idx1:])

        # check if we should skip this listing:
        skipped.append(False)
        if (not marked[-1]) and (not keywords[-1]):
            for i in range(len(skip_words)):
                if skip_words[i].lower() in cur_title.lower():
                    skipped[-1] = True
                    skipped_num[i] += 1

        # store to lists:
        links.append(cur_link)
        titles.append(cur_title)
        authors.append(cur_authors)
        crossref.append('(*cross-listing*)' in cur_listing)
        replaced.append('replaced with revised version' in cur_listing)

    # filter only marked listings:
    if send_marked_only:
        marked_or_keywords = [marked[i] or keywords[i] for i in range(len(marked))]
        links = [links[i] for i in range(len(links)) if marked_or_keywords[i]]
        titles = [titles[i] for i in range(len(titles)) if marked_or_keywords[i]]
        authors = [authors[i] for i in range(len(authors)) if marked_or_keywords[i]]
        crossref = [crossref[i] for i in range(len(crossref)) if marked_or_keywords[i]]
        replaced = [replaced[i] for i in range(len(replaced)) if marked_or_keywords[i]]

    # build reformatted message:
    msg_header = """<html>
                      <head></head>
                      <body>
                        <p><br>
                        """

    old_count = sum([replaced[i] or crossref[i] for i in range(len(replaced))])
    msg_header += "Today's <b>" + ttl + "</b> arXiv: " + str(len(titles) - old_count) + " new listings and " + \
                  str(old_count) + " updates (" + str(sum(replaced)) + " replacements + " + str(sum(crossref)) + \
                  " crossrefs). <br>"

    if sum(skipped) > 0:
        msg_header += 'Skipped ' + str(sum(skipped)) + ' listings: '
        for i in range(len(skip_words)):
            if skipped_num[i] > 0:
                msg_header += str(skipped_num[i]) + ' with "' + skip_words[i] + '", '
        msg_header = msg_header[:-2] + ". <br>"

    is_marked = sum(marked) > 0
    is_keyword = sum(keywords) > 0
    if not send_marked_only:
        if is_marked:
            msg_header += 'Notice listings' if sum(marked) > 1 else 'Notice listing'
            msg_header += ' Nr. ' + ', '.join([str(i + 1) for i in range(len(marked)) if marked[i]]) + ' by ' + \
                          ', '.join([mark_authors[i] for i in range(len(marked_num)) if marked_num[i]]) + ". <br>"
        if is_keyword:
            msg_header += 'Notice listings' if sum(keywords) > 1 else 'Notice listing'
            msg_header += ' Nr. ' + ', '.join([str(i + 1) for i in range(len(keywords)) if keywords[i]]) + ' with ' + \
                          ', '.join([mark_titles[i] for i in range(len(keywords_num)) if keywords_num[i]]) + ". <br>"

    else:  # send marked only
        msg_header += 'Only showing selected listings: <br>'
        if is_marked:
            msg_header += '* By ' + ', '.join([mark_authors[i] for i in range(len(marked_num)) if marked_num[i]]) + \
                          ". <br>"

        if is_keyword:
            msg_header += '* With ' + \
                          ', '.join(['"' + mark_titles[i] + '"' for i in range(len(keywords_num)) if keywords_num[i]]) \
                          + ". <br>"

    msg_body = '<br><br>'
    for idx in range(len(titles)):
        if not skipped[idx]:
            msg_body += 'Title ' + str(idx + 1) + ' out of ' + str(len(titles))

            if replaced[idx] and crossref[idx]:
                msg_body += ' (cross-listing, revised version)'
            elif replaced[idx]:
                msg_body += ' (revised version)'
            elif crossref[idx]:
                msg_body += ' (cross-listing)'

            msg_body += '<br><b>' + titles[idx] + '</b><br>by ' + authors[idx] + '<br>is at ' + \
                        '<a href="https://arxiv.org/abs/' + links[idx] + '">' + links[idx] + '</a><br><br><br>'

    msg_footer = """
            </p>
          </body>
        </html>
        """

    html_msg = msg_header + msg_body + msg_footer

    return html_msg, is_marked


def set_from_env(env_var_name: str, default_value):
    """
    Helper function to acquire parameters from the environment's secrets.
    :param env_var_name: name of the environment variable
    :param default_value: default value to use if the environment variable is not set, 'vital' will raise an error
    :return:
    """
    if env_var_name in os.environ:
        env_var = unstring(os.environ[env_var_name])
        if env_var is not None:
            return env_var
    else:
        if default_value == 'vital':
            raise Exception(f"Missing environment variable {env_var_name}")
    return default_value


def unstring(s: str):
    """
    Helper function to convert strings to their original type.
    :param s: string to convert
    :return: original type
    """
    if not len(s):
        return None
    elif s == 'True':
        return True
    elif s == 'False':
        return False
    elif s[0] == '[' and s[-1] == ']':
        return [unstring(x) for x in s[1:-1].split(', ')]
    elif (s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'"):
        return s[1:-1]
    else:
        return s


class ArxivReformatter:
    def __init__(self, email_username: str, email_password: str, trash_fetched=True):

        # email parameters:
        self.email_username = email_username
        self.email_password = email_password
        self.trash_fetched = trash_fetched

        # connect to the email server:
        self.mail_imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        self.mail_imap.login(self.email_username, self.email_password)
        self.mail_imap.select('Inbox')
        self.mail_smtp = smtplib.SMTP('smtp.gmail.com:587')
        self.mail_smtp.ehlo()
        self.mail_smtp.starttls()
        self.mail_smtp.login(self.email_username, self.email_password)

    def fetch_emails(self, from_arxiv=list) -> tuple:
        """
        Fetches emails from the arxiv server.
        :param from_arxiv: list of emails to fetch. If empty, finds emails.
        :return: tuple of (list of additional emails, first message, first message time).
        """

        # if no emails from arXiv were given, find them:
        if from_arxiv == ['first iteration'] or self.trash_fetched or (not from_arxiv):
            sts_msg, from_arxiv = self.mail_imap.search(None, 'FROM', '"no-reply@arxiv.org"')
            if sts_msg != 'OK':
                raise ValueError("Error searching Inbox.")

            from_arxiv = from_arxiv[0].split(b' ')

            # for msg_id in from_arxiv:  # debug before uncommenting
            #     labels = self.mail_imap.fetch(msg_id, '(X-GM-LABELS)')
            #     if b'reformatted' in labels[1][0]:
            #         from_arxiv.remove(msg_id)

        msg_id = from_arxiv[0]

        if not msg_id:
            return [], None, None

        # fetch the email body (RFC822) for the given ID:
        sts_msg, cur_msg = self.mail_imap.fetch(msg_id, '(RFC822)')
        if sts_msg != 'OK':
            raise ValueError("Error fetching mail.")
        cur_msg = cur_msg[0][1].decode()

        date_time_idx0 = cur_msg.find('\r\n', cur_msg.find('\r\n') + 1) + 10
        date_time_idx1 = cur_msg.find('\r\n', date_time_idx0 + 1) - 6
        date_time_str = cur_msg[date_time_idx0:date_time_idx1]
        date_time_dt = datetime.strptime(date_time_str, '%a, %d %b %Y %H:%M:%S %z').astimezone(timezone.utc)
        date_time = datetime.strftime(date_time_dt, '%a, %d %b %Y %H:%M:%S')

        return from_arxiv, cur_msg, date_time

    def send_email(self, msg, subject, recipients):
        """
        Send email with the given message.

        """

        email_message = MIMEMultipart('alternative')
        email_message['Subject'] = subject
        email_message['From'] = self.email_username
        email_message['To'] = ', '.join(recipients)
        msg_body = MIMEText(msg, 'html')
        email_message.attach(msg_body)

        # send email:
        self.mail_smtp.sendmail(self.email_username, recipients,
                                email_message.as_string())  # send the reformatted message

    def close_connection(self):
        """
        Close the connection to the email server.

        """

        self.mail_smtp.quit()
        self.mail_imap.close()
        self.mail_imap.logout()
