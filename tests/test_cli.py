import pytest

from corescope.cli import build_parser, main


def test_no_command_prints_help(capsys):
    assert main([]) == 0
    captured = capsys.readouterr()
    assert "corescope" in captured.out


def test_version_flag_exits_zero():
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--version"])
    assert exc_info.value.code == 0


def test_subcommands_registered():
    parser = build_parser()
    args = parser.parse_args(["bin", "/bin/true"])
    assert args.command == "bin"
    assert args.path == "/bin/true"


def test_unimplemented_subcommand_returns_error(capsys):
    assert main(["mem", "/tmp/does-not-exist.dmp"]) == 1
    captured = capsys.readouterr()
    assert "not implemented" in captured.err
