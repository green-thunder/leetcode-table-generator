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
        sanitized_title = title.lower().replace(" ", "_")
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

    def update_or_add_solutions(self, new_solutions):
        """
        Updates or adds new rows to the Markdown table at a specified index.
        If the index exists, appends new language solutions to the "Solution" column.
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
            index = solution.get("index", None)
            if index is None:
                index = int(input(f"Enter the index for the solution: "))

            slug = solution.get("slug", "")
            language = self.language_icons.get(solution["language"].lower(), solution["language"])
            link = self.create_leetcode_link(slug)

            row_found = False
            for j, line in enumerate(content[header_index + 2:], start=header_index + 2):
                if line.startswith("|"):
                    try:
                        existing_index = int(line.split("|")[1].strip())
                    except ValueError:
                        continue  # Skip lines that don't have a valid index
                    if existing_index == index:
                        # Existing row, update or append language solution
                        row_found = True
                        parts = line.strip().split("|")

                        # Retain existing title and difficulty
                        existing_title_md = parts[2].strip()
                        existing_title = self.extract_title_from_markdown(existing_title_md)
                        existing_solutions = parts[3].strip()
                        existing_difficulty = parts[4].strip()

                        # Use existing title if not provided
                        if "title" in solution and solution["title"].strip():
                            title = solution["title"]
                        else:
                            title = existing_title

                        # Use existing difficulty if not provided
                        if "difficulty" in solution and solution["difficulty"].strip():
                            difficulty = self.difficulty_emojis.get(
                                solution["difficulty"].lower(),
                                solution["difficulty"]
                            )
                        else:
                            difficulty = existing_difficulty

                        # Generate the solution file path
                        solution_path = self.format_solution_filename(title, index, solution["language"])

                        # Update solutions
                        if f"[{language}]({solution_path})" not in existing_solutions:
                            updated_solutions = f"{existing_solutions}, [{language}]({solution_path})"
                            parts[3] = f" {updated_solutions} "
                        else:
                            parts[3] = f" {existing_solutions} "  # No change

                        # Update title and difficulty in parts
                        parts[2] = f" [{title}]({link}) "
                        parts[4] = f" {difficulty} "

                        # Reconstruct the line
                        content[j] = "|".join(parts) + "\n"
                        break

            if not row_found:
                # Title and difficulty from solution or defaults
                title = solution.get("title", "Unknown Title")
                difficulty = self.difficulty_emojis.get(
                    solution.get("difficulty", "unknown").lower(),
                    solution.get("difficulty", "Unknown")
                )

                # Generate the solution file path
                solution_path = self.format_solution_filename(title, index, solution["language"])

                # Create a new row
                row = f"|{index} | [{title}]({link}) | [{language}]({solution_path}) | {difficulty} |\n"
                content.insert(header_index + 2, row)

        # Write updated content back to the file
        with open(self.file_path, 'w') as file:
            file.writelines(content)

        print(f"Updated {self.file_path} with new solutions!")
