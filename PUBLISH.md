# Publish the repository

The ChatGPT GitHub connector can write files to an existing repository but cannot create a new repository shell.

Create an empty **public** repository named `basilisk-quartet` under `PaulTiffany` without initializing a README, license, or `.gitignore`. Then either:

## From the Git bundle

```bash
git clone basilisk-quartet.bundle basilisk-quartet
cd basilisk-quartet
git remote add origin git@github.com:PaulTiffany/basilisk-quartet.git
git push -u origin main
```

## From the ZIP

Extract the ZIP, open a terminal in the folder, and run:

```bash
git init -b main
git add .
git commit -m "Stand up Basilisk Quartet and MAP-LB control protocol"
git remote add origin git@github.com:PaulTiffany/basilisk-quartet.git
git push -u origin main
```

After the shell exists, the connected assistant can also populate or revise the repository directly.
