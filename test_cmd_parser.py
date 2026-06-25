#!/usr/bin/env python3
"""Test command parser."""

import sys
sys.path.insert(0, '.')

from src.core.command_compiler import CommandParser, parse_command_line

# Test various command formats
tests = [
    ['agent'],
    ['agent', 'researcher'],
    ['agent', 'researcher', 'hello'],
    ['agent', 'research', 'quantum computing'],
    ['agent', 'write', 'AI trends'],
    ['research', 'Latest AI'],
    ['write', 'Technology', '--format', 'markdown'],
    ['list-tools'],
    ['list-agents'],
]

for test in tests:
    print(f'Testing: {" ".join(test)}')
    result = parse_command_line(test)
    print(f'  command: {result["command"]}')
    print(f'  subcommand: {result["subcommand"]}')
    print(f'  agent_name: {result["agent_name"]}')
    print(f'  prompt: {result["prompt"]}')
    print()
