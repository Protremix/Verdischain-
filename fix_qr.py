path = "lib/features/transactions/presentation/qr_scanner_page.dart"
with open(path, "r") as f:
    lines = f.readlines()

# Find and replace lines 99-116 (0-indexed: 98-115) which contain the ValueListenableBuilder
new_lines = []
i = 0
while i < len(lines):
    if "ValueListenableBuilder<TorchState>" in lines[i]:
        # Skip the entire ValueListenableBuilder block until we find the closing
        depth = 0
        while i < len(lines):
            if "ValueListenableBuilder<TorchState>" in lines[i]:
                depth += 1
            if ")," in lines[i] and depth > 0:
                depth -= 1
                if depth == 0:
                    break
            i += 1
        i += 1
        # Insert the replacement
        new_lines.append("                  CircleAvatar(\n")
        new_lines.append("                    backgroundColor: Colors.black.withOpacity(0.6),\n")
        new_lines.append("                    child: IconButton(\n")
        new_lines.append("                      icon: const Icon(Icons.flash_off, color: Colors.white),\n")
        new_lines.append("                      onPressed: () => _controller.toggleTorch(),\n")
        new_lines.append("                    ),\n")
        new_lines.append("                  ),\n")
        continue
    new_lines.append(lines[i])
    i += 1

with open(path, "w") as f:
    f.writelines(new_lines)

print("QR scanner fixed!")
