# 🐙 GH-Sutra: The Grammar of Collaboration

The journey of `git-sutra` was one of introspection. It was about taming the chaos within our local repositories, mastering our own history, and creating a personal grammar for version control. We had built a temple of logic and order, a place where every commit had its purpose. The internal dialogue was fluent, elegant, and powerful.

But code does not live in a temple. It lives in the world.

A new friction became apparent, not in our commits, but in the space between them. It was the friction of collaboration. The workflow was a constant, jarring dance of `Alt+Tab` between the command line—our sanctuary of focus—and the browser.

-   `git push`, then `Alt+Tab` to the browser.
-   Find the right repository.
-   Click "Compare & pull request".
-   Wait for the page to load.
-   Copy-paste commit messages into the description.
-   Click "Create pull request".
-   `Alt+Tab` back to the terminal.

Each step was a small cut in the fabric of concentration. Each context switch was a tax on deep work. We had perfected the art of writing the book, but we were still fumbling when it came time to send it to the publisher.

### The Bridge to the World: The GitHub CLI

The GitHub CLI (`gh`) was the bridge. It promised to bring the entire collaborative workflow—issues, pull requests, reviews—directly into our terminal, promising to end the context-switching tax.

And it did. But like vanilla Git, it was a set of powerful, atomic commands. It gave us the words—`pr`, `create`, `list`, `view`—but not the sentences. Typing `gh pr create --title "My Awesome Feature" --body "Here are the details..."` was functional, but it wasn't a conversation. It was a command, not an expression. The atoms were there, but the grammar was missing.

### From Tool to Fluent Language: Extending the Sutra

If `git-sutra` is the grammar of your internal thoughts, **`gh-sutra` is the grammar of your public conversation.**

It applies the exact same "Sutra" philosophy to the `gh` CLI. It's not about replacing commands; it's about weaving them together into a fluent language. It provides a layer of intelligent aliases and workflows that transform verbose, multi-step processes into single, intentional expressions. It's about turning a series of commands into a seamless dialogue with GitHub.

### The Architecture: A Unified Philosophy

To maintain the purity of the Sutra philosophy, the architecture of `gh-sutra` mirrors that of its sibling project.

#### 🧘 `gh-sutra-core`
Simple, high-impact shortcuts for everyday GitHub interactions. We applied the DRY principle here as well, creating a single `core.logic` file to act as the source of truth for all dependency-free aliases. This is the foundation for a faster, more fluid collaborative workflow.

#### 🚀 `gh-sutra-pro`
Interactive menus and advanced workflows for power users. This layer requires `fzf` to create powerful, searchable menus for navigating pull requests and issues. To formalize its unique purpose, we established the `.ghalias` extension for its templates. This creates a specific, namespaced grammar for GitHub collaboration, distinct from the local focus of `.gitalias`.

---

### Installation

Clone the repository containing the `gh-sutra` directory.

#### To Install Core:
- **Windows:** `.\gh-sutra-core\install.cmd`
- **Linux/macOS:** `sh ./gh-sutra-core/install.sh`

#### To Install Pro:
> **Prerequisite:** You must have `fzf` (a command-line fuzzy finder) installed.

- **Windows:** `.\gh-sutra-pro\install.cmd`
- **Linux/macOS:** `sh ./gh-sutra-pro/install.sh`

---
> The work is not done when the code is written. It is done when the code is shared, discussed, and merged into the collective human effort. This is the next step in our journey: transforming the command line from a place of execution into a place of conversation. Now, let's talk to the world. Fluently.
