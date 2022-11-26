# [arXiv reformatter](https://github.com/galNess/arxiv-reformatter)

This is a simple repo to reformat arXiv subscription emails into a more easily readable format.

![Usage examples](arxiv_reformatter.png)


## Key features
1. Strips abstracts.
2. Highlights listings from selected authors.
3. Skips listings with specified title words (clears some hype).
4. Handles two arXiv categories with individual parameters for each.


## Usage
The main idea is to use a dummy Gmail account to subscribe to arXiv with.
Then, you can fork this repo to your own gitHub account and use gitHub actions to automatically reformat the emails 
and send them to your own email.

1. Create a dummy Gmail account, and generate an [app password](https://support.google.com/accounts/answer/185833?hl=en)
   for it.
2. Subscribe to arXiv with this account (instructions on 
   [https://arxiv.org/help/subscribe](https://arxiv.org/help/subscribe)).
3. Fork this repo.
4. Go to the repo settings, and add the following secrets:
    - `EMAIL_USERNAME`: Email address of the dummy Gmail account, e.g., `yourdummyaccount@gmail.com`.
    - `EMAIL_PASSWORD`: App password of the dummy Gmail account, e.g., `your appp assw ordd`.
    - `EMAIL_RECIPIENTS_CS`: Address(es) you want to send the reformatted emails to, e.g.,
      `yourrealemail@gmail.com` or `["yourrealemail@gmail.com", "lazyfriend@gmail.com"]`.
      Note that the double quotes are necessary to define a list inside a string (that cast as an environment variable).
      Generally, *cs* sets the default values for any other undefined category.
    - `EMAIL_RECIPIENTS_PHYSICS`: **optional**. Address(es) to send *physics* arXiv emails to. If you don't specify
      this one, it follows `EMAIL_RECIPIENTS_CS`.
    - `TRASH_FETCHED_EMAILS`: **optional**, [default is `True`]. If you want to delete the emails from the dummy Gmail
      account after they are reformatted, set this to `True`. Otherwise, set it to `False`.
      This is not a secret, but it is simpler to set all parameters in the same way.
    - `MARK_CS`: **optional**. List of authors to mark in the email head (and bold in the body). Note to only use
      first and last names, e.g., `["John Doe", "Jane Doe"]`, and avoid middle names.
      Also here, as in the following parameters, note that the quotes are necessary to cast it in the string.
    - `MARK_PHYSICS`: **optional**. Same as `MARK_CS`, but for *physics* arXiv emails.
    - `ADVERTISE_MARKED`: **optional**, [default is `True`]. If you want to send emails that feature marked authors 
       also to the other mailing list.
    - `SKIP_CS`: **optional**. List of words in the title to skip from reformatting. This is useful if you want
      to skip some papers that you find irrelevant, .e.g., `["crypto", "vision"]`.
    - `SKIP_PHYSICS`: **optional**. Same as `SKIP_CS`, but for *physics* arXiv emails.
	- Note that **optional** parameters are, well, optional. But if you don't keep them in the environment make sure to
	  clear them from the `/.github/workflows/actions.yml` file too!
5. Go to the repo actions, and enable the workflow.
    - To dig deeper into the gitHub actions part, you can check out 
      [the template I forked](https://gitHub.com/patrickloeber/python-gitHub-action-template) to create this repo.
6. Enjoy!


## Specifics
Personally, I use this repo to reformat arXiv emails from both cs and physics and send them to my own email.
You can easily modify the code to suit your needs.

Currently, the action initiates twice every hour and gathers statistics on the email times from arXiv.
Later this can be used to trigger the action at more appropriate times.
GitHub’s free tier offers 2000 runtime minutes per month. One run takes about 20s, so it’s ~200 runs per day.

## Credit
* Repo by [Gal Ness](mailto:gness67@gmail.com), 2022. Source: [github.com/galNess/arxiv-reformatter](https://github.com/galNess/arxiv-reformatter).
* Modified from [python-gitHub-action-template](https://gitHub.com/patrickloeber/python-gitHub-action-template) fork due to [Patrick Loeber](https://github.com/patrickloeber).

## Last run status
[![run main.py](https://github.com/galNess/arxiv-reformatter/actions/workflows/actions.yml/badge.svg)](https://github.com/galNess/arxiv-reformatter/actions/workflows/actions.yml)
