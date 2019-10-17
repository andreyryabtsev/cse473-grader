# Grading Instructions

1. Collect all submissions from Canvas saving them as a zip
2. Save the project file as a zip.
3. Invoke `./grade.py path/to/submissions.zip path/to/project.zip [file1.py ... fileN.py]` where the last arguments are the files that students were expected to submit. Specifically:

PS1
```
$ ./grade.py submissions.zip search.zip searchAgents.py search.py
```
PS2
```
$ ./grade.py submissions.zip multiagent.zip multiAgents.py
```
PS3
```
$ ./grade.py submissions.zip reinforcement.zip valueIterationAgents.py qlearningAgents.py analysis.py
```
PS4
```
$ ./grade.py submissions.zip tracking.zip bustersAgents.py inference.py
```
4. Export and download the grades as CSV; open them in a table editor and add the scores from the script output.
5. Save the CSV, import/upload it to Canvas.