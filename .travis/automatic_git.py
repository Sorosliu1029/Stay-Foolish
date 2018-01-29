#!/usr/bin/python3
"""
Operate Git commands automatically
"""
import git
import os.path as osp
import sys

def get_changed_files(repo):
    changed_files = repo.index.diff(None)
    return {
        "untracked": repo.untracked_files,
        "modified": [item.a_path for item in changed_files if item.change_type == 'M']
    }

def main():
    argvs = sys.argv

    working_dir = osp.abspath(osp.curdir)
    repo = git.Repo(working_dir)

    # Step 1. Pull from origin remote repo
    pull_infos = repo.remote().pull()
    assert all((pull_info.name == 'origin/master' for pull_info in pull_infos))

    # Step 2. Get changed files in local repo
    changed_files = get_changed_files(repo)
    assert not changed_files['untracked']
    if not changed_files['modified']:
        print("Nothing modified, abort Git operation.")
        sys.exit(0)

    if len(argvs) < 2:
        assert 'README.md' in changed_files['modified']
    
    # Step 3. Add changed files for commit
    add_entries = repo.index.add(changed_files['modified'])
    assert add_entries

    # Step 4. Commit changes
    commit_message = argvs[1] if len(argvs) > 1 else 'Update README'
    c = repo.index.commit(commit_message)
    assert c.hexsha == repo.head.commit.hexsha

    # Step 5. Push to origin remote repo
    push_infos = repo.remote().push()
    assert all((push_info.local_ref.name == 'master' for push_info in push_infos))


if __name__ == '__main__':
    main()
