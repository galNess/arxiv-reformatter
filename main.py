from reformatter import *
import logging
import logging.handlers


# load parameters from environment secrets
email_username = set_from_env('EMAIL_USERNAME', 'vital')
email_password = set_from_env('EMAIL_PASSWORD', 'vital')
email_recipients_cs = set_from_env('EMAIL_RECIPIENTS_CS', 'vital')
email_recipients_physics = set_from_env('EMAIL_RECIPIENTS_PHYSICS', email_recipients_cs)
email_recipients_all = []  # generate unique list of recipients from all categories
email_recipients_all = [x for x in email_recipients_cs + email_recipients_physics if x not in email_recipients_all and
                        not email_recipients_all.append(x)]
trash_fetched = set_from_env('TRASH_FETCHED', False)
mark_cs = set_from_env('MARK_CS', None)
mark_physics = set_from_env('MARK_PHYSICS', mark_cs)
emph_cs = set_from_env('EMPH_CS', None)
emph_physics = set_from_env('EMPH_PHYSICS', emph_cs)
advertise_marked = set_from_env('ADVERTISE_MARKED', True)
send_marked_only = set_from_env('SEND_MARKED_ONLY', False)
skip_cs = set_from_env('SKIP_CS', None)
skip_physics = set_from_env('SKIP_PHYSICS', skip_cs)

# set logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

if __name__ == "__main__":
    # initialize the reformatter
    reformatter = ArxivReformatter(email_username, email_password, trash_fetched)

    # loop over emails
    from_arxiv = ['first iteration']
    while True:
        # fetch first email
        from_arxiv, cur_msg, date_time = reformatter.fetch_emails(from_arxiv)
        if cur_msg is None:  # no more arXiv emails
            break

        title = extract_email_category(cur_msg)
        msg_id = from_arxiv.pop(0)

        if title is None:
            logger.info(f'Email {msg_id} is not the daily arXiv digest.')
            if trash_fetched:
                reformatter.mail_imap.store(msg_id, '+X-GM-LABELS', '\\Trash')
            continue

        # reformat email
        if title == 'physics':
            html_msg, is_marked = reformat_email(msg=cur_msg, ttl=title, mark_authors=mark_physics,
                                                 mark_titles=emph_physics, skip_words=skip_physics,
                                                 send_marked_only=send_marked_only)
            email_recipients = email_recipients_physics
        else:
            html_msg, is_marked = reformat_email(msg=cur_msg, ttl=title, mark_authors=mark_cs,
                                                 mark_titles=emph_cs, skip_words=skip_cs,
                                                 send_marked_only=send_marked_only)
            email_recipients = email_recipients_cs

        if is_marked and advertise_marked:
            email_recipients = email_recipients_physics + email_recipients_cs

        # send email
        email_subject = title + " arXiv, " + date_time[5:16]
        reformatter.send_email(msg=html_msg, subject=email_subject, recipients=email_recipients)

        # archive (/ and delete) the original message from the server:
        reformatter.mail_imap.store(msg_id, '+FLAGS', '\\Deleted')  # send to archive
        # reformatter.mail_imap.store(msg_id, '+FLAGS', 'reformatted') # add 'reformatted' label - debug reading loop
        if trash_fetched:
            reformatter.mail_imap.store(msg_id, '+X-GM-LABELS', '\\Trash')

        # log the message
        logger.info(f"Fetched email from: {date_time}")

    # close the connection and logout
    reformatter.close_connection()
