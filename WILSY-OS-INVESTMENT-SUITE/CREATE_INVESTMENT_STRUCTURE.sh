#!/bin/bash

echo "📂 CREATING INVESTMENT SUITE STRUCTURE..."
echo ""

# Create directory structure
mkdir -p {01-Executive,02-Legal,03-Financial,04-Operational,05-Marketing,06-Internal}
mkdir -p 01-Executive/{Deck,OnePager,Teaser}
mkdir -p 02-Legal/{NDA,TermSheets,SAFE,Shareholder}
mkdir -p 03-Financial/{Projections,Valuation,CapTable,Returns}
mkdir -p 04-Operational/{Roadmap,Playbook,Team,Deployment}
mkdir -p 05-Marketing/{Pitch,Testimonials,CaseStudies,Media}
mkdir -p 06-Internal/{EmailTemplates,ResponseScripts,FollowUp}

echo "✅ Directory structure created:"
tree -L 2
