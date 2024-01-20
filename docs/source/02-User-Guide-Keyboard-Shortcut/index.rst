.. _user-guide-keyboard-shortcut:

User Guide - Keyboard Shortcut
==============================================================================
This document describes the keyboard shortcuts in the terminal UI.

``aws_resource_search`` uses `readchar <https://github.com/magmax/python-readchar>`_ to capture Keyboard event. It may behave differently on different OS and terminal. The following keyboard shortcuts are tested on Windows, MacOS and Linux. If you find any issue, please report it to `GitHub Issues <https://github.com/MacHu-GWU/aws_resource_search-project/issues/new?assignees=MacHu-GWU&labels=bug&projects=&template=bug-report.md&title=%5BBug%5D%3A+describe+the+bug+here>`_.

**Query Editing and Search**

- ⬆️: tap ``Ctrl + E`` or ``UP`` to move item selection up.
- ⏫: tap ``Ctrl + R`` to scroll item selection up. this is very helpful when you have a long list of search result.
- ⬇️: tap ``Ctrl + D`` or ``DOWN`` to move item selection down.
- ⏬: tap ``Ctrl + F`` to scroll item selection down. this is very helpful when you have a long list of search result.
- ⬅️: tap ``LEFT`` to move query input cursor to the left.
- ➡️: tap ``RIGHT`` to move query input cursor to the right.
- ⬅️: tap ``LEFT`` to move query input cursor to the left.
- ➡️: tap ``RIGHT`` to move query input cursor to the right.
- ⏪: tap ``Alt + LEFT`` to move query input cursor to the previous word.
- ⏩: tap ``Alt + Right`` to move query input cursor to the next word.
- ⏮️: tap ``HOME`` to move query input cursor to the beginning of the line.
- ⏭️: tap ``RIGHT`` to move query input cursor to the end of the line.
- 🗑️⏪: tap ``Ctrl + K`` to delete the previous word.
- 🗑⏩: tap ``Ctrl + L`` to delete the next word.
- ↩️: tap ``Ctrl + X`` to clear the query input. this is very helpful when you want to start over.
- 🗑⬅: tap ``BACKSPACE`` to delete query input backward.
- 🗑️➡: tap ``DELETE`` to delete query input forward.
- 🔴: tap ``Ctrl + C`` to quit the app.

**User defined action**

- 🌐: tap ``Enter`` to open AWS console url in web browser. this action is available in most of AWS resource search result and detail view.
- 📋: tap ``Ctrl + A`` to copy ARN (AWS Resource Name) to clipboard. in detail view, it will copy the value of the detail.
- 🚀: tap ``Ctrl + W`` to perform custom user action. this is an not implemented action reserved for future extension.
- 🔗: tap ``Ctrl + U`` to copy AWS console url to clipboard. this action is useful when the app environment doesn't have a web browser.
- 👀: tap ``Ctrl + P`` to view more details about this resource.
- ⏪: tap ``Ctrl + B`` to clear the query of the current AWS resource type, so you can enter another query without typnig the resource type name.
- 🚪: tap ``F1`` to quit the the "viewing details" sub session.

**Special action**

- 🔁: enter ``!~`` anytime to refresh the query cache.
- 👀: enter ``!?`` anytime to view current AWS account info.
- 📌: enter ``!@`` anytime to view select another AWS profile.
- 🛠: enter ``!{`` anytime to view edit the ``${HOME}/.aws_resource_search/config.json`` file.
