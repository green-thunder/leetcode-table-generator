import os
import re

class SolutionUpdater:
    def __init__(self, file_path):
        self.file_path = file_path
        self.difficulty_emojis = {
            "easy": "🟢 Easy",
            "medium": "🟠 Medium",
            "hard": "🔴 Hard"
        }
        self.language_icons = {
            "python": "🐍 Python",
            "javascript": "🌐 JavaScript",
            "java": "☕ Java",
            "c++": "🔷 C++",
            "c#": "🎯 C#",
            "go": "🐹 Go",
            "ruby": "💎 Ruby",
            "php": "🐘 PHP",
            "swift": "🍎 Swift",
            "kotlin": "🚀 Kotlin",
            "rust": "🦀 Rust",
            "c": "🔵 C"
        }
        self.file_extensions = {
            "python": "py",
            "javascript": "js",
            "java": "java",
            "c++": "cpp",
            "c#": "cs",
            "go": "go",
            "ruby": "rb",
            "php": "php",
            "swift": "swift",
            "kotlin": "kt",
            "rust": "rs",
            "c": "c"
        }

    def format_solution_filename(self, title, index, language):
        """
        Formats the solution file name dynamically based on the title, index, and language.
        """
        extension = self.file_extensions.get(language.lower(), "")
        sanitized_title = re.sub(r'\W+', '_', title.lower()).strip('_')  # Remove non-word characters
        if not sanitized_title:
            sanitized_title = 'solution'  # Default name if title is empty after sanitization
        directory = f"Algorithms/{language.lower()}/"
        filename = f"{sanitized_title}_{index}.{extension}"
        return os.path.join(directory, filename)

    def create_leetcode_link(self, slug):
        """
        Constructs the full LeetCode link from the problem slug.
        """
        base_url = "https://leetcode.com/problems/"
        return f"{base_url}{slug}/"

    def extract_title_from_markdown(self, markdown_link):
        """
        Extracts the title from a markdown link.
        """
        match = re.match(r'\s*\[(.*?)\]\(.*?\)\s*', markdown_link)
        return match.group(1) if match else "Unknown Title"

    def generate_slug_from_title(self, title):
        """
        Generates a LeetCode slug dynamically from a problem title.
        """
        slug = re.sub(r'\s+', '-', title.strip())  # Replace spaces with hyphens
        slug = re.sub(r'[^\w\-]', '', slug)  # Remove special characters except hyphens
        return slug.lower()

    def extract_difficulty_from_display(self, difficulty_display):
        """
        Extracts the difficulty level from the display string.
        """
        for key, value in self.difficulty_emojis.items():
            if value == difficulty_display:
                return key.capitalize()
        return difficulty_display

    def map_difficulty_input(self, difficulty_input):
        """
        Maps user input to difficulty level.
        Accepts full words or first letters (E/e, M/m, H/h).
        """
        difficulty_input = difficulty_input.strip().lower()
        if difficulty_input in ['e', 'easy']:
            return 'Easy'
        elif difficulty_input in ['m', 'medium']:
            return 'Medium'
        elif difficulty_input in ['h', 'hard']:
            return 'Hard'
        else:
            print("Invalid difficulty input. Please enter 'Easy', 'Medium', or 'Hard' (or 'E', 'M', 'H').")
            return None  # Signal that the input was invalid

    def update_or_add_solutions(self, new_solutions):
        """
        Updates or adds new rows to the Markdown table at a specified index.
        If the index exists, appends new language solutions to the "Solution" column.
        Ensures the rows are sorted by the index.
        """
        # Read existing file
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                content = file.readlines()
        else:
            content = []

        # Find table start
        header_index = None
        for i, line in enumerate(content):
            if line.strip().startswith("|#"):
                header_index = i
                break

        # Ensure the header exists
        if header_index is None:
            content.append("|#      | Title | Solution | Difficulty |\n")
            content.append("|-------|-------|----------|------------|\n")
            header_index = len(content) - 2

        # Format new solutions
        for solution in new_solutions:
            # Prompt for missing index
            index = solution.get("index", None)
            if index is None:
                index = int(input(f"Enter the index for the problem in leetcode: "))

            # Initialize variables
            title = solution.get("title", "").strip()
            difficulty = solution.get("difficulty", "").strip()
            slug = solution.get("slug", "").strip()
            language = solution.get("language", "").strip()

            # Flags to check if existing row is found
            existing_row_found = False
            existing_title = None
            existing_difficulty_display = None

            # Search for existing row to extract missing data
            for j, line in enumerate(content[header_index + 2:], start=header_index + 2):
                if line.startswith("|"):
                    try:
                        existing_index = int(line.split("|")[1].strip())
                    except ValueError:
                        continue  # Skip lines that don't have a valid index
                    if existing_index == index:
                        # Existing row found
                        existing_row_found = True
                        parts = line.strip().split("|")
                        existing_title_md = parts[2].strip()
                        existing_title = self.extract_title_from_markdown(existing_title_md)
                        existing_difficulty_display = parts[4].strip()
                        break

            # Use existing title if not provided
            if not title:
                if existing_title:
                    title = existing_title
                else:
                    title = input(f"Enter the title for problem #{index}: ").strip()

            # Generate slug if not provided
            if not slug:
                slug = self.generate_slug_from_title(title)

            # Prompt for missing language
            if not language:
                language = input(f"Enter the language for solution #{index} (e.g., Python, Java): ").strip()
                if not language:
                    language = 'Python'  # Default to Python if user inputs nothing

            # Format language display
            language_display = self.language_icons.get(language.lower(), language)

            # Use existing difficulty if not provided
            if not difficulty:
                if existing_difficulty_display:
                    difficulty = self.extract_difficulty_from_display(existing_difficulty_display)
                else:
                    while True:
                        difficulty_input = input(f"Enter the difficulty of problem #{index} (Easy, Medium, Hard): ").strip()
                        mapped_difficulty = self.map_difficulty_input(difficulty_input)
                        if mapped_difficulty:
                            difficulty = mapped_difficulty
                            break

            # Format difficulty display
            difficulty_display = self.difficulty_emojis.get(difficulty.lower(), difficulty)

            # Generate LeetCode link and solution file path
            link = self.create_leetcode_link(slug)
            solution_path = self.format_solution_filename(title, index, language)

            # Now, proceed to update or add the row
            if existing_row_found:
                # Update existing row
                parts[2] = f" [{title}]({link}) "
                existing_solutions = parts[3].strip()
                if f"[{language_display}]({solution_path})" not in existing_solutions:
                    if existing_solutions:
                        updated_solutions = f"{existing_solutions}, [{language_display}]({solution_path})"
                    else:
                        updated_solutions = f"[{language_display}]({solution_path})"
                    parts[3] = f" {updated_solutions} "
                else:
                    parts[3] = f" {existing_solutions} "
                parts[4] = f" {difficulty_display} "
                content[j] = "|".join(parts) + "\n"
            else:
                # Add new row
                row = f"|{index} | [{title}]({link}) | [{language_display}]({solution_path}) | {difficulty_display} |\n"
                content.insert(header_index + 2, row)

        # Sort the table rows by index
        table_rows = content[header_index + 2:]
        sorted_rows = sorted(table_rows, key=lambda x: int(x.split("|")[1].strip()))
        content = content[:header_index + 2] + sorted_rows

        # Write updated content back to the file
        with open(self.file_path, 'w') as file:
            file.writelines(content)

        print(f"Updated {self.file_path} with new solutions!")
