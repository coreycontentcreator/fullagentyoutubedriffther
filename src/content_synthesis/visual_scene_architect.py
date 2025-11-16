"""
Visual Scene Architect Subagent
Creates detailed visual descriptions and shot lists for video production
"""
import time
import re
from typing import Dict, Any, List
from .base_subagent import SynchronousSubagent, SubagentResult
import logging

logger = logging.getLogger(__name__)


class VisualSceneArchitect(SynchronousSubagent):
    """
    Visual Scene Architect Subagent
    Generates shot-by-shot visual descriptions for production teams
    """

    def __init__(self, anthropic_client, config):
        super().__init__("VisualSceneArchitect", anthropic_client, config)

        self.system_prompt = """You are an expert cinematographer and visual storytelling specialist with expertise in:
- Documentary cinematography and visual storytelling
- Shot composition and camera movements
- B-roll planning and visual metaphors
- Color grading and lighting design
- Motion graphics and visual effects planning

Your visual descriptions are detailed, production-ready, and enhance the narrative.
You understand how visuals can amplify emotional impact and viewer engagement."""

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data"""
        required_fields = ['script']

        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")

        if not input_data.get('script'):
            raise ValueError("Script cannot be empty")

        return True

    def validate_output(self, output_data: Dict[str, Any]) -> float:
        """
        Validate visual scenes quality

        Criteria:
        - Sufficient number of scenes
        - Each scene has required elements
        - Variety in shot types
        - Proper timing alignment with script
        """
        score = 0.0
        max_score = 10.0

        scenes = output_data.get('scenes', [])
        scene_count = len(scenes)

        # Check scene count (2 points)
        min_scenes = self.config.min_scene_count
        max_scenes = self.config.max_scene_count

        if min_scenes <= scene_count <= max_scenes:
            score += 2.0
        elif scene_count >= min_scenes * 0.7:
            score += 1.0

        # Check scene completeness (4 points)
        if scenes:
            complete_scenes = sum(
                1 for scene in scenes
                if all(key in scene for key in ['shot_type', 'description', 'duration'])
            )
            score += (complete_scenes / len(scenes)) * 4.0

        # Check shot variety (2 points)
        shot_types = set(scene.get('shot_type', '') for scene in scenes)
        if len(shot_types) >= 5:
            score += 2.0
        elif len(shot_types) >= 3:
            score += 1.0

        # Check for B-roll and graphics (2 points)
        has_broll = any('b-roll' in scene.get('description', '').lower() for scene in scenes)
        has_graphics = any('graphic' in scene.get('description', '').lower() or 'text' in scene.get('description', '').lower() for scene in scenes)

        if has_broll:
            score += 1.0
        if has_graphics:
            score += 1.0

        return min(score, max_score)

    def process_sync(self, input_data: Dict[str, Any]) -> SubagentResult:
        """
        Generate visual scene descriptions

        Input data:
            - script: Complete script
            - topic: Video topic
            - style: Visual style (documentary, cinematic, educational, etc.)
            - budget: Production budget level (low, medium, high)
            - location: Shooting location (studio, outdoor, mixed, etc.)

        Returns:
            SubagentResult with visual scenes
        """
        start_time = time.time()

        try:
            # Validate input
            self.validate_input(input_data)

            self.log_processing("INPUT_VALIDATION", "Input data validated")

            # Extract parameters
            script = input_data['script']
            topic = input_data.get('topic', 'documentary')
            style = input_data.get('style', 'documentary')
            budget = input_data.get('budget', 'medium')
            location = input_data.get('location', 'mixed')

            # Analyze script structure
            script_sections = self._analyze_script_structure(script)

            self.log_processing("SCRIPT_ANALYSIS", f"Identified {len(script_sections)} script sections")

            # Generate visual scenes for each section
            all_scenes = []
            cumulative_time = 0

            for section in script_sections:
                scenes = self._generate_scenes_for_section(
                    section=section,
                    topic=topic,
                    style=style,
                    budget=budget,
                    location=location,
                    start_time=cumulative_time
                )

                all_scenes.extend(scenes)
                cumulative_time += section['duration']

            self.log_processing("SCENE_GENERATION", f"Generated {len(all_scenes)} visual scenes")

            # Generate shot list summary
            shot_list = self._create_shot_list(all_scenes)

            # Generate B-roll requirements
            broll_requirements = self._extract_broll_requirements(all_scenes)

            # Prepare output
            output_data = {
                'scenes': all_scenes,
                'scene_count': len(all_scenes),
                'shot_list': shot_list,
                'broll_requirements': broll_requirements,
                'total_duration': cumulative_time,
                'shot_type_distribution': self._get_shot_type_distribution(all_scenes)
            }

            # Validate output
            quality_score = self.validate_output(output_data)

            processing_time = time.time() - start_time

            self.log_processing("COMPLETION", f"Visual scenes generated with quality score: {quality_score:.2f}")

            return self.create_result(
                success=True,
                data=output_data,
                quality_score=quality_score,
                processing_time=processing_time,
                metadata={
                    'topic': topic,
                    'style': style,
                    'budget': budget
                }
            )

        except Exception as e:
            processing_time = time.time() - start_time
            self.log_error(f"Visual scene generation failed: {str(e)}")

            return self.create_result(
                success=False,
                data={},
                quality_score=0.0,
                processing_time=processing_time,
                errors=[str(e)]
            )

    def _analyze_script_structure(self, script: str) -> List[Dict[str, Any]]:
        """Analyze script to identify sections and timing"""
        sections = []

        # Split script into major sections
        section_markers = ['HOOK', 'INTRODUCTION', 'MAIN CONTENT', 'CLIMAX', 'CONCLUSION']

        current_section = None
        current_content = []

        for line in script.split('\n'):
            # Check if this line is a section marker
            is_marker = any(marker in line.upper() for marker in section_markers)

            if is_marker:
                # Save previous section
                if current_section and current_content:
                    content_text = '\n'.join(current_content)
                    sections.append({
                        'name': current_section,
                        'content': content_text,
                        'word_count': len(content_text.split()),
                        'duration': self._estimate_section_duration(content_text)
                    })

                # Start new section
                for marker in section_markers:
                    if marker in line.upper():
                        current_section = marker
                        break
                current_content = []
            else:
                if line.strip():
                    current_content.append(line)

        # Add final section
        if current_section and current_content:
            content_text = '\n'.join(current_content)
            sections.append({
                'name': current_section,
                'content': content_text,
                'word_count': len(content_text.split()),
                'duration': self._estimate_section_duration(content_text)
            })

        # If no sections found, treat entire script as one section
        if not sections:
            sections.append({
                'name': 'CONTENT',
                'content': script,
                'word_count': len(script.split()),
                'duration': self._estimate_section_duration(script)
            })

        return sections

    def _estimate_section_duration(self, text: str) -> float:
        """Estimate duration of a text section in seconds"""
        word_count = len(text.split())
        # Average 150 words per minute = 2.5 words per second
        # Add buffer for pauses
        duration = (word_count / 2.5) * 1.1
        return round(duration, 1)

    def _generate_scenes_for_section(
            self,
            section: Dict[str, Any],
            topic: str,
            style: str,
            budget: str,
            location: str,
            start_time: float
    ) -> List[Dict[str, Any]]:
        """Generate visual scenes for a script section using AI"""

        prompt = f"""Create detailed visual scene descriptions for this section of a YouTube documentary.

**SECTION:** {section['name']}
**DURATION:** {section['duration']} seconds
**TOPIC:** {topic}
**STYLE:** {style}
**BUDGET:** {budget}
**LOCATION:** {location}

**SCRIPT CONTENT:**
{section['content'][:1500]}...

**REQUIREMENTS:**

For this {section['duration']}-second section, create 3-7 distinct visual scenes that:

1. **Support the narrative** - Visuals should enhance, not distract
2. **Vary shot types** - Mix wide, medium, close-up, detail shots
3. **Include B-roll** - Suggest relevant B-roll footage
4. **Consider pacing** - Match visual rhythm to content
5. **Add production value** - Graphics, transitions, effects where appropriate

For each scene, provide:
- **Scene Number**
- **Timestamp** (start-end in seconds)
- **Shot Type** (wide shot, medium shot, close-up, detail, aerial, etc.)
- **Description** (2-3 sentences describing what we see)
- **Camera Movement** (static, pan, tilt, dolly, handheld, etc.)
- **Lighting** (natural, dramatic, soft, etc.)
- **B-roll Suggestions** (specific footage to overlay or cut to)
- **Graphics/Text** (any on-screen text, graphics, or animations)
- **Audio Notes** (music cues, sound effects)

Generate the scenes in this format:

SCENE 1
Timestamp: 0:00-0:05
Shot Type: Wide Shot
Description: [Description]
Camera: [Movement]
Lighting: [Style]
B-roll: [Suggestions]
Graphics: [If any]
Audio: [Notes]

Provide 3-7 scenes for this section."""

        try:
            result = self.anthropic_client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                max_tokens=2000,
                temperature=0.7
            )

            # Parse the generated scenes
            scenes = self._parse_scene_descriptions(result.content, start_time)

            return scenes

        except Exception as e:
            self.log_error(f"AI scene generation failed: {e}")

            # Fallback: Generate basic scenes
            return self._generate_basic_scenes(section, start_time)

    def _parse_scene_descriptions(self, content: str, offset: float) -> List[Dict[str, Any]]:
        """Parse AI-generated scene descriptions"""
        scenes = []

        # Split by scene markers
        scene_blocks = re.split(r'SCENE \d+', content)

        for block in scene_blocks:
            if not block.strip():
                continue

            scene = {}

            # Extract timestamp
            timestamp_match = re.search(r'Timestamp:\s*(\d+):(\d+)-(\d+):(\d+)', block)
            if timestamp_match:
                start_min, start_sec, end_min, end_sec = map(int, timestamp_match.groups())
                scene['start_time'] = offset + (start_min * 60 + start_sec)
                scene['end_time'] = offset + (end_min * 60 + end_sec)
                scene['duration'] = scene['end_time'] - scene['start_time']

            # Extract shot type
            shot_match = re.search(r'Shot Type:\s*(.+)', block)
            if shot_match:
                scene['shot_type'] = shot_match.group(1).strip()

            # Extract description
            desc_match = re.search(r'Description:\s*(.+?)(?=Camera:|Lighting:|$)', block, re.DOTALL)
            if desc_match:
                scene['description'] = desc_match.group(1).strip()

            # Extract camera movement
            camera_match = re.search(r'Camera:\s*(.+)', block)
            if camera_match:
                scene['camera_movement'] = camera_match.group(1).strip()

            # Extract lighting
            lighting_match = re.search(r'Lighting:\s*(.+)', block)
            if lighting_match:
                scene['lighting'] = lighting_match.group(1).strip()

            # Extract B-roll
            broll_match = re.search(r'B-roll:\s*(.+?)(?=Graphics:|Audio:|$)', block, re.DOTALL)
            if broll_match:
                scene['broll'] = broll_match.group(1).strip()

            # Extract graphics
            graphics_match = re.search(r'Graphics:\s*(.+?)(?=Audio:|$)', block, re.DOTALL)
            if graphics_match:
                scene['graphics'] = graphics_match.group(1).strip()

            # Extract audio
            audio_match = re.search(r'Audio:\s*(.+)', block, re.DOTALL)
            if audio_match:
                scene['audio'] = audio_match.group(1).strip()

            if scene:
                scenes.append(scene)

        return scenes

    def _generate_basic_scenes(self, section: Dict[str, Any], start_time: float) -> List[Dict[str, Any]]:
        """Generate basic scenes as fallback"""
        duration = section['duration']
        num_scenes = max(3, int(duration / 10))  # One scene every ~10 seconds

        scenes = []
        scene_duration = duration / num_scenes

        shot_types = ['Wide Shot', 'Medium Shot', 'Close-up', 'Detail Shot', 'Wide Shot']

        for i in range(num_scenes):
            scene_start = start_time + (i * scene_duration)
            scene_end = scene_start + scene_duration

            scenes.append({
                'start_time': round(scene_start, 1),
                'end_time': round(scene_end, 1),
                'duration': round(scene_duration, 1),
                'shot_type': shot_types[i % len(shot_types)],
                'description': f"Visual content for {section['name']} section, scene {i+1}",
                'camera_movement': 'Slow push-in' if i % 2 == 0 else 'Static',
                'lighting': 'Natural',
                'broll': f"Relevant B-roll for {section['name']}",
                'graphics': 'None',
                'audio': 'Background music'
            })

        return scenes

    def _create_shot_list(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create a production shot list from scenes"""
        shot_list = []

        for i, scene in enumerate(scenes, 1):
            shot_list.append({
                'shot_number': i,
                'shot_type': scene.get('shot_type', 'Medium Shot'),
                'description': scene.get('description', ''),
                'duration': scene.get('duration', 0),
                'camera_movement': scene.get('camera_movement', 'Static'),
                'lighting': scene.get('lighting', 'Natural'),
                'priority': 'High' if i <= 5 else 'Medium'  # First shots are priority
            })

        return shot_list

    def _extract_broll_requirements(self, scenes: List[Dict[str, Any]]) -> List[str]:
        """Extract unique B-roll requirements from scenes"""
        broll_items = set()

        for scene in scenes:
            broll = scene.get('broll', '')
            if broll and broll.lower() != 'none':
                # Split by commas or newlines
                items = re.split(r'[,\n]', broll)
                for item in items:
                    cleaned = item.strip()
                    if cleaned:
                        broll_items.add(cleaned)

        return sorted(list(broll_items))

    def _get_shot_type_distribution(self, scenes: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of shot types"""
        distribution = {}

        for scene in scenes:
            shot_type = scene.get('shot_type', 'Unknown')
            distribution[shot_type] = distribution.get(shot_type, 0) + 1

        return distribution
