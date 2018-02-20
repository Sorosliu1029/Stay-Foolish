#!/bin/sh

setup_git() {
  git config user.email "soros.liu1029@gmail.com"
  git config user.name "Soros Liu"
}

commit() {
  git checkout master
  git add README.md data/*.json docs/index.html
  git commit --message "Updated. Travis build: $TRAVIS_BUILD_NUMBER.[skip ci]"
}

upload_files() {
  git remote add origin-github https://${GH_TOKEN}@github.com/Sorosliu1029/Stay-Foolish.git > /dev/null 2>&1
  git push --quiet --set-upstream origin-github master
}

setup_git
commit
upload_files
echo "Push succeed."
