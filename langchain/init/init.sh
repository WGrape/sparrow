#!/bin/sh

# no source command, so use `. ~/.bashrc` to reload refresh.
if grep -qF 'export OPENAI_API_KEY=' ~/.bashrc; then
    sed -i 's/^export OPENAI_API_KEY=.*$/export OPENAI_API_KEY="sk-please-reset-OPENAI_API_KEY-variable-inside-the-container-manually"/' /etc/profile;
    . /etc/profile
else
    echo 'export OPENAI_API_KEY="sk-please-reset-OPENAI_API_KEY-variable-inside-the-container-manually"' >> /etc/profile
    . /etc/profile
fi
