"""
Scriptwriter Subagent
Generates complete, production-ready scripts with viral optimization
"""
import time
from typing import Dict, Any, List, Optional
from .base_subagent import SynchronousSubagent, SubagentResult
import logging

logger = logging.getLogger(__name__)


class ScriptArchitect(SynchronousSubagent):
    """
    Script Architect Subagent
    Creates production-ready scripts optimized for engagement and retention
    """

    def __init__(self, anthropic_client, config):
        super().__init__("ScriptArchitect", anthropic_client, config)

        # System prompt for script generation
        self.system_prompt = """You are an elite YouTube documentary scriptwriter with expertise in:
- Viral content creation and audience retention
- Academic research presentation in engaging formats
- Psychological triggers for engagement
- Documentary storytelling and narrative structure

Your scripts are production-ready, engaging, and optimized for maximum viewer retention.
You understand how to hook viewers in the first 15 seconds and keep them watching until the end."""

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for script generation"""
        required_fields = ['topic', 'research_data']

        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")

        if not input_data.get('topic'):
            raise ValueError("Topic cannot be empty")

        return True

    def validate_output(self, output_data: Dict[str, Any]) -> float:
        """
        Validate script quality and calculate score

        Criteria:
        - Length appropriate (5000-15000 words)
        - Has all required sections
        - Hook is compelling
        - Flow is logical
        - CTAs are present
        """
        score = 0.0
        max_score = 10.0

        script = output_data.get('script', '')

        # Check length (2 points)
        word_count = len(script.split())
        min_length = self.config.min_script_length
        max_length = self.config.max_script_length

        if min_length <= word_count <= max_length:
            score += 2.0
        elif word_count >= min_length * 0.8:
            score += 1.0

        # Check required sections (3 points)
        required_sections = ['hook', 'introduction', 'main content', 'conclusion']
        sections_present = sum(1 for section in required_sections if section.lower() in script.lower())
        score += (sections_present / len(required_sections)) * 3.0

        # Check for engagement elements (3 points)
        has_questions = '?' in script
        has_hooks = any(phrase in script.lower() for phrase in ['imagine', 'what if', 'discover', 'you won\'t believe'])
        has_cta = any(phrase in script.lower() for phrase in ['subscribe', 'like', 'comment', 'share'])

        if has_questions:
            score += 1.0
        if has_hooks:
            score += 1.0
        if has_cta:
            score += 1.0

        # Check structure (2 points)
        paragraphs = script.split('\n\n')
        if len(paragraphs) >= 10:  # Well-structured
            score += 2.0
        elif len(paragraphs) >= 5:
            score += 1.0

        return min(score, max_score)

    def process_sync(self, input_data: Dict[str, Any]) -> SubagentResult:
        """
        Generate complete script

        Input data:
            - topic: Video topic
            - research_data: Research findings and citations
            - target_audience: Target audience description
            - video_duration: Target duration in minutes
            - tone: Script tone (engaging, authoritative, casual, etc.)
            - style: Documentary, educational, narrative, etc.
            - viral_strategy: Optional viral strategy data
            - hooks: Optional hook suggestions

        Returns:
            SubagentResult with generated script
        """
        start_time = time.time()

        try:
            # Validate input
            self.validate_input(input_data)

            self.log_processing("INPUT_VALIDATION", "Input data validated successfully")

            # Extract parameters
            topic = input_data['topic']
            research_data = input_data.get('research_data', {})
            target_audience = input_data.get('target_audience', 'general audience')
            video_duration = input_data.get('video_duration', self.config.target_video_duration)
            tone = input_data.get('tone', 'engaging but authoritative')
            style = input_data.get('style', 'documentary')
            viral_strategy = input_data.get('viral_strategy', {})
            hooks = input_data.get('hooks', [])

            # Build comprehensive prompt
            prompt = self._build_script_prompt(
                topic=topic,
                research_data=research_data,
                target_audience=target_audience,
                video_duration=video_duration,
                tone=tone,
                style=style,
                viral_strategy=viral_strategy,
                hooks=hooks
            )

            self.log_processing("PROMPT_GENERATION", f"Generated prompt ({len(prompt)} chars)")

            # Generate script using Anthropic
            result = self.anthropic_client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                max_tokens=self.config.max_script_length // 2,  # Rough token estimate
                temperature=0.7
            )

            script = result.content

            self.log_processing("SCRIPT_GENERATION", f"Generated script ({len(script)} chars, {len(script.split())} words)")

            # Post-process script
            script = self._post_process_script(script)

            # Extract metadata
            metadata = self._extract_script_metadata(script)

            # Prepare output
            output_data = {
                'script': script,
                'word_count': len(script.split()),
                'character_count': len(script),
                'estimated_duration': self._estimate_duration(script),
                'sections': metadata['sections'],
                'hook_count': metadata['hook_count'],
                'cta_count': metadata['cta_count'],
                'tokens_used': result.tokens_used
            }

            # Validate output
            quality_score = self.validate_output(output_data)

            processing_time = time.time() - start_time

            self.log_processing("COMPLETION", f"Script generated with quality score: {quality_score:.2f}")

            return self.create_result(
                success=True,
                data=output_data,
                quality_score=quality_score,
                processing_time=processing_time,
                metadata={
                    'model': result.model,
                    'topic': topic,
                    'target_audience': target_audience,
                    'video_duration': video_duration
                }
            )

        except Exception as e:
            processing_time = time.time() - start_time
            self.log_error(f"Script generation failed: {str(e)}")

            return self.create_result(
                success=False,
                data={},
                quality_score=0.0,
                processing_time=processing_time,
                errors=[str(e)]
            )

    def _build_script_prompt(
            self,
            topic: str,
            research_data: Dict[str, Any],
            target_audience: str,
            video_duration: int,
            tone: str,
            style: str,
            viral_strategy: Dict[str, Any],
            hooks: List[str]
    ) -> str:
        """Build comprehensive prompt for script generation"""

        # Extract research insights
        key_findings = research_data.get('key_findings', [])
        citations = research_data.get('citations', [])
        unique_insights = research_data.get('unique_insights', [])

        # Extract viral elements
        psychology_triggers = viral_strategy.get('psychology_triggers', [])
        retention_strategy = viral_strategy.get('retention_strategy', {})
        engagement_moments = viral_strategy.get('engagement_moments', [])

        # Build hook section
        hook_section = ""
        if hooks:
            hook_section = f"""
Suggested Hooks (choose the best or create a better one):
{chr(10).join(f'- {hook}' for hook in hooks[:5])}
"""

        # Build research section
        research_section = ""
        if key_findings:
            research_section = f"""
Key Research Findings to Include:
{chr(10).join(f'- {finding}' for finding in key_findings[:10])}
"""

        # Build psychology triggers section
        psychology_section = ""
        if psychology_triggers:
            psychology_section = f"""
Psychology Triggers to Implement:
{chr(10).join(f'- {trigger}' for trigger in psychology_triggers[:8])}
"""

        prompt = f"""Create a complete, production-ready YouTube documentary script about:

**TOPIC:** {topic}

**TARGET AUDIENCE:** {target_audience}
**VIDEO DURATION:** {video_duration} minutes (~{video_duration * 150} words)
**TONE:** {tone}
**STYLE:** {style}

{hook_section}

{research_section}

{psychology_section}

**SCRIPT STRUCTURE REQUIREMENTS:**

1. **OPENING HOOK (0-15 seconds):**
   - Grab attention immediately
   - Create curiosity gap or present shocking fact
   - Make a bold promise or ask compelling question
   - DO NOT introduce yourself or the channel yet

2. **INTRODUCTION (15-45 seconds):**
   - Briefly introduce the topic
   - Explain why it matters to the viewer
   - Preview what they'll learn
   - Build anticipation

3. **MAIN CONTENT (80% of video):**
   - Present research findings in engaging narrative
   - Use storytelling techniques (not just facts)
   - Include specific examples and case studies
   - Break into clear sections with transitions
   - Place "mini-hooks" every 2 minutes to maintain retention
   - Use questions to engage viewers
   - Incorporate psychology triggers naturally

4. **MID-ROLL HOOKS (every 2 minutes):**
   - Tease upcoming content
   - Ask provocative questions
   - Present surprising facts
   - Create anticipation for next section

5. **CLIMAX/REVELATION (last 20%):**
   - Present the most important/surprising finding
   - Tie everything together
   - Answer the main question posed at start

6. **CONCLUSION (last 30-60 seconds):**
   - Summarize key takeaways (3-5 points)
   - Call to action (subscribe, like, comment)
   - Leave with memorable final thought

**WRITING GUIDELINES:**

- Write in {tone} voice
- Use active voice and present tense when possible
- Vary sentence length for rhythm
- Include rhetorical questions
- Use analogies and metaphors for complex concepts
- Write for the ear, not the eye (conversational)
- Include [PAUSE] markers for dramatic effect
- Mark visual cues in [BRACKETS] for production team
- Ensure facts are accurate (cite sources in production notes, not script)

**ENGAGEMENT TECHNIQUES:**

- Start sentences with "You", "Imagine", "What if"
- Use specific numbers and data points
- Create contrast and comparison
- Build and release tension
- Use the rule of three
- Include unexpected twists or revelations

**QUALITY STANDARDS:**

- Every sentence must serve a purpose
- No filler or fluff
- Tight, punchy writing
- Clear progression of ideas
- Strong opening and closing

Generate the COMPLETE script now. Make it exceptional."""

        return prompt

    def _post_process_script(self, script: str) -> str:
        """Clean up and format generated script"""

        # Remove multiple blank lines
        while '\n\n\n' in script:
            script = script.replace('\n\n\n', '\n\n')

        # Ensure proper spacing after sections
        script = script.strip()

        # Add section markers if not present
        if '# HOOK' not in script and '## HOOK' not in script:
            # Try to identify the hook (first paragraph)
            parts = script.split('\n\n')
            if parts:
                parts[0] = f"## OPENING HOOK\n\n{parts[0]}"
                script = '\n\n'.join(parts)

        return script

    def _extract_script_metadata(self, script: str) -> Dict[str, Any]:
        """Extract metadata from generated script"""

        # Count sections
        sections = []
        for marker in ['HOOK', 'INTRODUCTION', 'MAIN CONTENT', 'CONCLUSION', 'CLIMAX']:
            if marker in script.upper():
                sections.append(marker)

        # Count hooks (look for question marks and hook phrases)
        hook_count = script.count('?')
        hook_count += sum(script.lower().count(phrase) for phrase in ['imagine', 'what if', 'you won\'t believe'])

        # Count CTAs
        cta_count = sum(script.lower().count(phrase) for phrase in ['subscribe', 'like', 'comment', 'share', 'hit the bell'])

        return {
            'sections': sections,
            'hook_count': hook_count,
            'cta_count': cta_count,
            'paragraph_count': len(script.split('\n\n')),
            'sentence_count': script.count('.') + script.count('!') + script.count('?')
        }

    def _estimate_duration(self, script: str) -> float:
        """
        Estimate video duration from script
        Average speaking rate: 150 words per minute
        """
        word_count = len(script.split())
        # Account for pauses and visual sections
        adjusted_word_count = word_count * 0.9
        duration_minutes = adjusted_word_count / 150

        return round(duration_minutes, 1)
