# BodhiKit Privacy Policy

Effective date: September 28, 2026

BodhiKit is an open-source, local-first learning plugin. The BodhiKit publisher
does not operate a server for the plugin, and the plugin does not send learner
data anywhere. The only data the publisher receives is what someone chooses to
submit to the optional feedback survey described below.

## Data handled by the plugin

When the host provides a writable project filesystem, BodhiKit may read and
write learning plans, progress, review schedules, reflection notes, revision
sheets, and other files inside the learner's selected project. These files
remain under the learner's control. BodhiKit's bundled scripts do not send them
to the publisher or to a third-party service.

When a host does not expose local project storage, BodhiKit works within the
current conversation and does not claim that learning state was persisted.
Conversation content is handled by the host platform under that platform's
privacy policy and account settings.

## Permissions and network access

BodhiKit may request access to read and write files in the selected project and
to run its bundled local state scripts. Codex may also run the packaged
lifecycle hooks after the user reviews and trusts them. The plugin does not
require network access, advertising identifiers, analytics, or tracking.

## Optional feedback survey

The publisher runs an anonymous feedback survey on Google Forms. Its questions
are listed in [docs/survey.md](./docs/survey.md). It is linked from the README,
from GitHub's "New issue" page, and by `/evaluate` once at a project milestone.
The plugin never opens the link, never submits anything, and never asks during
a lesson; answering is entirely up to you.

The survey does not require signing in and does not collect an email address
unless you type one into the optional email question. Answers are stored
in the publisher's Google account under Google's privacy policy, are used only
to improve BodhiKit, and are never published individually; anything shared
from them is aggregated and anonymized. To have your answers deleted, ask through
GitHub Discussions and describe your answer closely enough to identify it.

## Retention and deletion

The publisher retains no plugin data. Learners control retention of their local
project files and conversation history. Local BodhiKit data can be removed by
deleting the relevant learning project or its `.bodhi` directory. Uninstalling
the plugin stops future plugin activity but does not automatically delete
learner-created project files.

## Children and sensitive data

BodhiKit is a general educational tool and is not designed to collect personal
or sensitive information. Do not place secrets, credentials, regulated data,
or information about children in learning files or prompts unless the selected
host and workspace are approved for that use.

## Changes and contact

Material changes to BodhiKit's data practices will be documented here before a
release that uses them. Questions or privacy requests can be opened through
[BodhiKit GitHub Discussions](https://github.com/AnjanJ/bodhikit/discussions).
