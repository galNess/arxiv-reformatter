# [arXiv reformatter](https://github.com/galNess/arxiv-reformatter)

| This is a simple repo to reformat arXiv subscription emails into a more easily readable format. |
|-------------------------------------------------------------------------------------------------|


![Usage examples](arxiv_reformatter.png)


## Key features
1. Strip abstracts.
2. Highlight listings from selected authors or with specific keywords in their titles.
3. Skip listings with specified title words (clears some hype), or even send only marked listings.
4. Handle two arXiv categories with individual parameters for each.


## Usage
The main idea is to use a dummy Gmail account to subscribe to arXiv with.
Then, you can fork this repo to your own gitHub account and use gitHub actions to automatically reformat the emails 
and send them to your own email.

1. Create a dummy Gmail account, and generate an [app password](https://support.google.com/accounts/answer/185833?hl=en)
   for it.
2. Subscribe to arXiv with this account (instructions on 
   [https://arxiv.org/help/subscribe](https://arxiv.org/help/subscribe)).
3. Fork this repo.
4. Add the following secrets by going to the repo settings, under `Security` -> `Secrets` -> `Actions` ->
   `New repository secret` (green button @ top right).
    - `EMAIL_USERNAME`: Email address of the dummy Gmail account, e.g., `yourdummyaccount@gmail.com`.
    - `EMAIL_PASSWORD`: App password of the dummy Gmail account, e.g., `your appp assw ordd`.
    - `EMAIL_RECIPIENTS_CS`: Address(es) you want to send the reformatted emails to, e.g.,
      `yourrealemail@gmail.com` or `["yourrealemail@gmail.com", "lazyfriend@gmail.com"]`.
      Note that the double quotes are necessary to define a list inside a string (that cast as an environment variable).
      Generally, *cs* sets the default values for any other undefined category.
    - `EMAIL_RECIPIENTS_PHYSICS`: **optional**. Address(es) to send *physics* arXiv emails to. If you don't specify
      this one, it follows `EMAIL_RECIPIENTS_CS`.
    - `TRASH_FETCHED_EMAILS`: **optional**, [default is `False`]. If you want to delete the emails from the dummy Gmail
      account after they are reformatted, set this to `True`.

    This (and the following) are not really secrets, but it is simpler to set all parameters in the same way.
    If you want to be able to see the content (or just lazy), you can alternatively tweak it and update the values
    directly in `main.py` (lines 25-33) or at `.github/workflows/actions.yml` (lines 28-36).
    - `MARK_CS`: **optional**. List of authors to mark in the email head (and bold in the body). Note to only use
      first and last names, e.g., `["John Doe", "Jane Doe"]`, and avoid middle names.
      Also here, as in the following parameters, note that the quotes are necessary to cast it in the string.
    - `MARK_PHYSICS`: **optional**. Same as `MARK_CS`, but for *physics* arXiv emails.
    - `EMPH_CS`: **optional**. List of words to highlight in the listing titles, i.e., your research interests.
    - `EMPH_PHYSICS`: **optional**. Same as `EMPH_CS`, but for *physics* arXiv emails.
    - `ADVERTISE_MARKED`: **optional**, [default is `True`]. If you want to send emails that feature marked authors 
       also to the other mailing list.
    - `SEND_MARKED_ONLY`: **optional**, [default is `False`]. Only include listings with highlights (authors or titles)
       in the reformatted email.
    - `SEND_NEW_ONLY`: **optional**, [default is `False`]. Only include listings that are not updates (replacements).
    - `SKIP_CS`: **optional**. List of words in the title to skip from reformatting. This is useful if you want
      to skip some papers that you find irrelevant, .e.g., `["crypto", "vision"]`.
    - `SKIP_PHYSICS`: **optional**. Same as `SKIP_CS`, but for *physics* arXiv emails.
5. Go to the repo actions, and enable the workflow:
    - In `Actions` tab (not the `Actions` within the `Settings` one), click the green enabling button.
    - Go to `run main.py` on the left bar (under `Actions`), then click `Enable workflow` on the right.
    - To dig deeper into the gitHub actions part, you can check out 
      [the template I forked](https://gitHub.com/patrickloeber/python-gitHub-action-template) to create this repo.
6. Enjoy!


## Specifics
Personally, I use this repo to reformat arXiv emails from both cs and physics and send them to my own email.
You can easily modify the code to suit your needs.

Currently, the action initiates twice every hour and gathers statistics on the email times from arXiv.
Later this can be used to trigger the action at more appropriate times.
GitHub’s free tier offers 2000 runtime minutes per month. One run takes about 20s, so it’s ~200 runs per day.


## Easy upgrades
If you want to contribute, please consider:
1. Moving some non-sensitive secrets to a CSV (or other) external file. Optimally, it will not be duplicated to forked repositories.
2. Adding keyword marks also in abstract text (easy).
3. Moving highlighted listings to the top of the list. 
4. Handling reply emails. For example, it can be smooth to add new keywords by emailing back the dummy address.

A more extensive upgrade would be to ditch the original digest emails and work directly with the [arXiv API](https://arxiv.org/help/api/).


## Credits
* Repo by [Gal Ness](https://github.com/galNess), 2022.
* Modified from [python-gitHub-action-template](https://gitHub.com/patrickloeber/python-gitHub-action-template) fork due to [Patrick Loeber](https://github.com/patrickloeber).
* Source: [github.com/galNess/arxiv-reformatter](https://github.com/galNess/arxiv-reformatter).

Feel free to share, fork and modify this repo to your needs!


## Last run status
[![run main.py](../..//actions/workflows/actions.yml/badge.svg)](../../actions/workflows/actions.yml)

