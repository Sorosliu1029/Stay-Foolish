#!/bin/sh

setup_git() {
  git config user.email "soros.liu1029@gmail.com"
  git config user.name "Soros Liu"
}

commit() {
  git checkout travis
  git add README.md books.json
  git commit --message "Update readme. Travis build: $TRAVIS_BUILD_NUMBER"
}

upload_files() {
  git remote add origin-github https://${GH_TOKEN}@github.com/Sorosliu1029/Stay-Foolish.git > /dev/null 2>&1
  git push --quiet --set-upstream origin-github travis
}

setup_git
commit
upload_files
echo "Push succeed."