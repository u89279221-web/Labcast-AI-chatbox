import glob
import re

for filepath in glob.glob("tests/test_*.py"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "import os" not in content:
        content = "import os\n" + content
    
    # Replace sqlite URL with os.environ.get
    content = content.replace('"sqlite:///:memory:"', 'os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")')
    
    # Replace connect_args
    content = content.replace(
        'connect_args={"check_same_thread": False}', 
        'connect_args={"check_same_thread": False} if "sqlite" in os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:") else {}'
    )
    
    # Replace poolclass
    content = content.replace(
        'poolclass=StaticPool',
        'poolclass=StaticPool if "sqlite" in os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:") else None'
    )
    
    # Add drop_all before create_all, matching the same indentation
    def replacer(match):
        indent = match.group(1)
        return f"{indent}SQLModel.metadata.drop_all(engine)\n{indent}SQLModel.metadata.create_all(engine)"
        
    content = re.sub(r"^(\s*)SQLModel\.metadata\.create_all\(engine\)", replacer, content, flags=re.MULTILINE)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
