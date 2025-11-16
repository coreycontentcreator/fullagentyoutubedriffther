"""
Production Notes Generator Subagent
Creates comprehensive production guidance and notes for video creators
"""
import time
from typing import Dict, Any, List
from .base_subagent import SynchronousSubagent, SubagentResult
import logging

logger = logging.getLogger(__name__)


class ProductionNotesGenerator(SynchronousSubagent):
    """
    Production Notes Generator Subagent
    Generates detailed production notes, technical requirements, and creator guidance
    """

    def __init__(self, anthropic_client, config):
        super().__init__("ProductionNotesGenerator", anthropic_client, config)

        self.system_prompt = """You are an experienced video production consultant specializing in:
- YouTube content production workflows
- Technical requirements and equipment recommendations
- Post-production guidance and editing notes
- Resource allocation and timeline planning
- Quality control and optimization

Your production notes are comprehensive, actionable, and tailored to the creator's resources."""

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data"""
        required_fields = ['script', 'visual_scenes']

        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")

        return True

    def validate_output(self, output_data: Dict[str, Any]) -> float:
        """
        Validate production notes quality

        Criteria:
        - Has all key sections
        - Equipment list is comprehensive
        - Timeline is realistic
        - Budget estimate provided
        - Post-production notes included
        """
        score = 0.0
        max_score = 10.0

        # Check for required sections (5 points)
        required_sections = [
            'equipment_requirements',
            'production_timeline',
            'budget_estimate',
            'shooting_checklist',
            'post_production_notes'
        ]

        sections_present = sum(1 for section in required_sections if section in output_data)
        score += (sections_present / len(required_sections)) * 5.0

        # Check equipment list (2 points)
        equipment = output_data.get('equipment_requirements', {})
        if equipment:
            has_camera = 'camera' in equipment
            has_audio = 'audio' in equipment
            has_lighting = 'lighting' in equipment

            if has_camera and has_audio and has_lighting:
                score += 2.0
            elif has_camera or has_audio:
                score += 1.0

        # Check timeline (2 points)
        timeline = output_data.get('production_timeline', {})
        if timeline:
            has_phases = len(timeline) >= 3
            has_estimates = any('duration' in v or 'days' in str(v).lower() for v in timeline.values())

            if has_phases and has_estimates:
                score += 2.0
            elif has_phases:
                score += 1.0

        # Check checklists (1 point)
        checklist = output_data.get('shooting_checklist', [])
        if len(checklist) >= 5:
            score += 1.0

        return min(score, max_score)

    def process_sync(self, input_data: Dict[str, Any]) -> SubagentResult:
        """
        Generate production notes

        Input data:
            - script: Complete script
            - visual_scenes: Visual scene descriptions
            - budget_level: Production budget (low, medium, high)
            - crew_size: Size of crew (solo, small, medium, large)
            - location: Shooting location
            - deadline: Production deadline

        Returns:
            SubagentResult with production notes
        """
        start_time = time.time()

        try:
            # Validate input
            self.validate_input(input_data)

            self.log_processing("INPUT_VALIDATION", "Input data validated")

            # Extract parameters
            script = input_data['script']
            visual_scenes = input_data['visual_scenes']
            budget_level = input_data.get('budget_level', 'medium')
            crew_size = input_data.get('crew_size', 'small')
            location = input_data.get('location', 'mixed')
            deadline = input_data.get('deadline', '2 weeks')

            # Generate equipment requirements
            equipment = self._generate_equipment_requirements(
                visual_scenes, budget_level, location
            )

            self.log_processing("EQUIPMENT", f"Generated equipment list with {len(equipment)} categories")

            # Generate production timeline
            timeline = self._generate_production_timeline(
                script, visual_scenes, crew_size, deadline
            )

            self.log_processing("TIMELINE", "Generated production timeline")

            # Generate budget estimate
            budget = self._estimate_budget(equipment, crew_size, len(visual_scenes))

            # Generate shooting checklist
            checklist = self._generate_shooting_checklist(visual_scenes, location)

            # Generate post-production notes
            post_production = self._generate_post_production_notes(
                script, visual_scenes, budget_level
            )

            # Generate optimization tips
            optimization_tips = self._generate_optimization_tips(
                budget_level, crew_size, len(visual_scenes)
            )

            # Prepare output
            output_data = {
                'equipment_requirements': equipment,
                'production_timeline': timeline,
                'budget_estimate': budget,
                'shooting_checklist': checklist,
                'post_production_notes': post_production,
                'optimization_tips': optimization_tips,
                'location_requirements': self._extract_location_requirements(visual_scenes),
                'talent_requirements': self._extract_talent_requirements(script),
                'risk_assessment': self._assess_production_risks(visual_scenes, budget_level, deadline)
            }

            # Validate output
            quality_score = self.validate_output(output_data)

            processing_time = time.time() - start_time

            self.log_processing("COMPLETION", f"Production notes generated with quality score: {quality_score:.2f}")

            return self.create_result(
                success=True,
                data=output_data,
                quality_score=quality_score,
                processing_time=processing_time,
                metadata={
                    'budget_level': budget_level,
                    'crew_size': crew_size,
                    'scene_count': len(visual_scenes)
                }
            )

        except Exception as e:
            processing_time = time.time() - start_time
            self.log_error(f"Production notes generation failed: {str(e)}")

            return self.create_result(
                success=False,
                data={},
                quality_score=0.0,
                processing_time=processing_time,
                errors=[str(e)]
            )

    def _generate_equipment_requirements(
            self,
            visual_scenes: List[Dict[str, Any]],
            budget_level: str,
            location: str
    ) -> Dict[str, List[str]]:
        """Generate equipment requirements based on scenes and budget"""

        equipment = {
            'camera': [],
            'audio': [],
            'lighting': [],
            'accessories': [],
            'optional': []
        }

        # Camera requirements
        if budget_level == 'high':
            equipment['camera'] = [
                'Cinema camera (RED, ARRI, Sony FX series)',
                'Multiple lens set (wide, standard, telephoto)',
                'External recorder (Atomos Ninja)',
                'ND filters kit'
            ]
        elif budget_level == 'medium':
            equipment['camera'] = [
                'DSLR/Mirrorless (Sony A7, Canon R6)',
                '2-3 quality lenses (24-70mm, 70-200mm)',
                'ND filters',
                'Extra batteries and memory cards'
            ]
        else:
            equipment['camera'] = [
                'Entry DSLR/Mirrorless or smartphone with gimbal',
                'One versatile lens (24-105mm)',
                'ND filter',
                'Extra batteries and SD cards'
            ]

        # Audio requirements
        equipment['audio'] = [
            'Lavalier microphone',
            'Shotgun microphone',
            'Audio recorder (Zoom H6 or similar)',
            'Windscreen/deadcat for outdoor',
            'Headphones for monitoring'
        ]

        # Lighting requirements
        if location in ['studio', 'indoor']:
            if budget_level == 'high':
                equipment['lighting'] = [
                    'Professional LED panel kit (Aputure 300d or similar)',
                    'Softboxes and diffusion',
                    'RGB accent lights',
                    'C-stands and sandbags'
                ]
            else:
                equipment['lighting'] = [
                    'Basic LED panel kit (2-3 lights)',
                    'Reflectors and diffusers',
                    'Light stands'
                ]

        # Accessories
        equipment['accessories'] = [
            'Tripod (fluid head recommended)',
            'Gimbal/stabilizer for movement shots',
            'Backdrop or greenscreen (if applicable)',
            'Teleprompter (for talking head segments)'
        ]

        # Optional based on scenes
        equipment['optional'] = [
            'Drone for aerial shots',
            'Slider for smooth camera movement',
            'Multiple camera bodies for multi-angle',
            'Color charts for grading reference'
        ]

        return equipment

    def _generate_production_timeline(
            self,
            script: str,
            visual_scenes: List[Dict[str, Any]],
            crew_size: str,
            deadline: str
    ) -> Dict[str, str]:
        """Generate production timeline"""

        scene_count = len(visual_scenes)

        timeline = {
            'pre_production': f"3-5 days: Location scouting, equipment rental, talent booking",
            'shooting': f"{max(1, scene_count // 20)}-{max(2, scene_count // 10)} days: Principal photography",
            'post_production': f"5-10 days: Editing, color grading, sound design",
            'review_revisions': f"2-3 days: Client review and revisions",
            'final_delivery': f"1 day: Final export and upload",
            'total_estimated': deadline
        }

        return timeline

    def _estimate_budget(
            self,
            equipment: Dict[str, List[str]],
            crew_size: str,
            scene_count: int
    ) -> Dict[str, Any]:
        """Estimate production budget"""

        budget = {
            'equipment_rental': 0,
            'crew_labor': 0,
            'location_fees': 0,
            'post_production': 0,
            'misc': 0,
            'total': 0
        }

        # Calculate based on crew size
        crew_multipliers = {'solo': 1, 'small': 2, 'medium': 4, 'large': 8}
        multiplier = crew_multipliers.get(crew_size, 2)

        base_equipment = len([item for items in equipment.values() for item in items]) * 50
        budget['equipment_rental'] = base_equipment * multiplier

        budget['crew_labor'] = 500 * multiplier
        budget['location_fees'] = 200 if scene_count > 50 else 100
        budget['post_production'] = 800 * multiplier
        budget['misc'] = 200

        budget['total'] = sum(v for k, v in budget.items() if k != 'total')

        budget['range'] = f"${int(budget['total'] * 0.8):,} - ${int(budget['total'] * 1.2):,}"

        return budget

    def _generate_shooting_checklist(
            self,
            visual_scenes: List[Dict[str, Any]],
            location: str
    ) -> List[str]:
        """Generate pre-shoot checklist"""

        checklist = [
            "✓ All equipment tested and batteries charged",
            "✓ Memory cards formatted and backup storage ready",
            "✓ Location permissions and permits secured",
            "✓ Shot list printed and distributed to crew",
            "✓ Talent briefed on schedule and expectations",
            "✓ Backup equipment prepared",
            "✓ Weather checked (for outdoor shoots)",
            "✓ Audio levels tested in location",
            "✓ Lighting setup planned and tested",
            "✓ Props and set dressing prepared",
            "✓ Call sheets distributed to all crew",
            "✓ Backup power sources available"
        ]

        return checklist

    def _generate_post_production_notes(
            self,
            script: str,
            visual_scenes: List[Dict[str, Any]],
            budget_level: str
    ) -> Dict[str, Any]:
        """Generate post-production guidance"""

        notes = {
            'editing_software': 'Adobe Premiere Pro, DaVinci Resolve, or Final Cut Pro X',
            'workflow': [
                '1. Organize and label all footage by scene',
                '2. Create rough cut following script structure',
                '3. Add B-roll and visual overlays',
                '4. Fine-tune pacing and transitions',
                '5. Add music and sound effects',
                '6. Color grade for consistency',
                '7. Mix audio (dialogue, music, SFX)',
                '8. Add graphics and text overlays',
                '9. Final review and export'
            ],
            'color_grading': 'Apply cinematic LUT, adjust exposure and contrast, match shots for consistency',
            'audio_mixing': 'Dialogue -12dB to -6dB, Music -20dB to -18dB, SFX as needed for impact',
            'graphics_needed': [
                'Lower thirds for expert names/credentials',
                'Data visualization for statistics',
                'Transition graphics between sections',
                'Thumbnail and end screen'
            ],
            'music_notes': 'Use royalty-free music from Artlist, Epidemic Sound, or Audio Library',
            'export_settings': {
                'resolution': '1920x1080 (1080p) or 3840x2160 (4K)',
                'frame_rate': '24fps (cinematic) or 30fps (standard)',
                'codec': 'H.264 for YouTube',
                'bitrate': '20-50 Mbps for 1080p, 50-100 Mbps for 4K'
            }
        }

        return notes

    def _generate_optimization_tips(
            self,
            budget_level: str,
            crew_size: str,
            scene_count: int
    ) -> List[str]:
        """Generate optimization tips"""

        tips = [
            "Batch similar shots together to minimize setup changes",
            "Shoot extra B-roll - you can never have too much",
            "Record room tone for audio editing",
            "Take photos of setups for continuity",
            "Keep detailed notes of take numbers and issues",
            "Review footage on-set before moving to next location",
            "Have a backup plan for each critical shot",
            "Schedule most important shots when energy is highest"
        ]

        if budget_level == 'low':
            tips.append("Use natural light when possible to save on equipment")
            tips.append("Consider smartphone apps for affordable production tools")

        if crew_size == 'solo':
            tips.append("Use tripod for all shots - don't try to handhold")
            tips.append("Record test takes to check framing and audio")

        return tips

    def _extract_location_requirements(self, visual_scenes: List[Dict[str, Any]]) -> List[str]:
        """Extract location requirements from scenes"""
        locations = set()

        for scene in visual_scenes:
            desc = scene.get('description', '').lower()

            if 'outdoor' in desc or 'outside' in desc:
                locations.add('Outdoor location')
            if 'indoor' in desc or 'inside' in desc or 'studio' in desc:
                locations.add('Indoor/studio space')
            if 'office' in desc:
                locations.add('Office environment')
            if 'nature' in desc or 'forest' in desc or 'park' in desc:
                locations.add('Natural setting')

        return list(locations) if locations else ['General purpose location']

    def _extract_talent_requirements(self, script: str) -> List[str]:
        """Extract talent/actor requirements from script"""
        requirements = []

        script_lower = script.lower()

        if 'narrator' in script_lower or 'voiceover' in script_lower:
            requirements.append('Narrator/Voiceover artist')

        if 'host' in script_lower or 'presenter' in script_lower:
            requirements.append('On-camera host/presenter')

        if 'interview' in script_lower or 'expert' in script_lower:
            requirements.append('Subject matter experts for interviews')

        if not requirements:
            requirements.append('Voiceover narrator (can be creator)')

        return requirements

    def _assess_production_risks(
            self,
            visual_scenes: List[Dict[str, Any]],
            budget_level: str,
            deadline: str
    ) -> List[Dict[str, str]]:
        """Assess production risks"""

        risks = []

        scene_count = len(visual_scenes)

        if scene_count > 100:
            risks.append({
                'risk': 'High scene count',
                'severity': 'Medium',
                'mitigation': 'Consider reducing scenes or extending timeline'
            })

        if budget_level == 'low' and scene_count > 50:
            risks.append({
                'risk': 'Budget constraints vs. scope',
                'severity': 'High',
                'mitigation': 'Prioritize essential scenes, use stock footage for others'
            })

        if 'week' in deadline.lower() and '1' in deadline:
            risks.append({
                'risk': 'Tight deadline',
                'severity': 'High',
                'mitigation': 'Focus on pre-production planning, have backup plans'
            })

        # Check for weather-dependent shoots
        outdoor_scenes = sum(1 for scene in visual_scenes if 'outdoor' in scene.get('description', '').lower())
        if outdoor_scenes > scene_count * 0.3:
            risks.append({
                'risk': 'Weather-dependent outdoor shoots',
                'severity': 'Medium',
                'mitigation': 'Have indoor backup options, check extended forecast'
            })

        if not risks:
            risks.append({
                'risk': 'Standard production risks',
                'severity': 'Low',
                'mitigation': 'Follow checklist and maintain communication'
            })

        return risks
