import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml
from pandas.errors import EmptyDataError

from .types import PipelineResult, AgentStatus
from agents.inspector.inspector_agent import InspectorAgent
from agents.refiner.cleaner_agent import CleanerAgent
from agents.insight.insight_agent import InsightAgent


class DataPipeline:
    """
    Main orchestrator for the agentic data pipeline
    """
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self._setup_logging()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize agents
        self.inspector = InspectorAgent(self.config['agents']['inspector']['config'])
        self.cleaner = CleanerAgent(self.config['agents']['refiner']['config'])
        self.insight_agent = InsightAgent(
            self.config['agents']['insight']['config'],
            self.config['data']['artifacts_path']
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        level = getattr(logging, log_config.get('level', 'INFO'))
        
        # Create artifacts directory if it doesn't exist
        artifacts_path = self.config['data']['artifacts_path']
        os.makedirs(artifacts_path, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=level,
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            handlers=[
                logging.FileHandler(log_config.get('file', 'pipeline.log')),
                logging.StreamHandler()
            ]
        )
    
    def run_pipeline(self, input_file: str) -> PipelineResult:
        """
        Run the complete data pipeline
        """
        start_time = time.time()
        errors = []
        
        self.logger.info(f"Starting pipeline execution for file: {input_file}")
        
        try:
            # Load data
            data = self._load_data(input_file)
            self.logger.info(f"Loaded data with shape: {data.shape}")
            
            # Step 1: Inspect data
            quality_report = None
            if self.config['agents']['inspector']['enabled']:
                self.logger.info("Running Inspector Agent...")
                quality_report = self.inspector.analyze_data(data)
                self.logger.info(f"Data quality assessment: {quality_report.overall_quality.value}")
            
            # Step 2: Clean data
            cleaning_report = None
            cleaned_data = data
            if self.config['agents']['refiner']['enabled']:
                self.logger.info("Running Refiner Agent...")
                cleaned_data, cleaning_report = self.cleaner.clean_data(data)
                self.logger.info(f"Data cleaned: {cleaning_report.original_shape} -> {cleaning_report.cleaned_shape}")
            
            # Step 3: Generate insights
            insight_report = None
            if self.config['agents']['insight']['enabled']:
                self.logger.info("Running Insight Agent...")
                insight_report = self.insight_agent.generate_insights(cleaned_data)
                self.logger.info(f"Generated {len(insight_report.plots_generated)} visualizations")
            
            # Save cleaned data
            output_file = self._save_cleaned_data(cleaned_data, input_file)
            
            execution_time = time.time() - start_time
            
            result = PipelineResult(
                status=AgentStatus.COMPLETED,
                input_file=input_file,
                output_file=output_file,
                quality_report=quality_report,
                cleaning_report=cleaning_report,
                insight_report=insight_report,
                execution_time=execution_time,
                errors=errors
            )
            
            self.logger.info(f"Pipeline completed successfully in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            errors.append(str(e))
            self.logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            
            execution_time = time.time() - start_time
            
            return PipelineResult(
                status=AgentStatus.FAILED,
                input_file=input_file,
                output_file=None,
                quality_report=None,
                cleaning_report=None,
                insight_report=None,
                execution_time=execution_time,
                errors=errors
            )
    
    def _load_data(self, file_path: str) -> pd.DataFrame:
        """Load data from various file formats"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.csv':
            # Try different encodings and separators
            encodings = ['utf-8', 'latin-1', 'cp1252']
            separators = [',', ';', '\t']
            
            for encoding in encodings:
                for sep in separators:
                    try:
                        data = pd.read_csv(file_path, encoding=encoding, sep=sep)
                        if data.shape[1] >= 1:
                            self.logger.info(f"Loaded CSV with encoding: {encoding}, separator: '{sep}'")
                            return self._ensure_non_empty(data, file_path)
                    except EmptyDataError as exc:
                        raise ValueError(f"Input file '{file_path}' is empty or has no parsable columns") from exc
                    except Exception:
                        continue
            
            try:
                data = pd.read_csv(file_path)
                return self._ensure_non_empty(data, file_path)
            except EmptyDataError as exc:
                raise ValueError(f"Input file '{file_path}' is empty or has no parsable columns") from exc
            
        elif file_extension in ['.xlsx', '.xls']:
            data = pd.read_excel(file_path)
        elif file_extension == '.json':
            data = pd.read_json(file_path)
        elif file_extension == '.parquet':
            data = pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

        return self._ensure_non_empty(data, file_path)

    def _ensure_non_empty(self, data: pd.DataFrame, file_path: str) -> pd.DataFrame:
        """Raise a descriptive error if the dataframe is empty."""
        if data.empty:
            raise ValueError(f"Input file '{file_path}' is empty after parsing. Please provide a file with data.")
        return data
    
    def _save_cleaned_data(self, data: pd.DataFrame, original_file: str) -> str:
        """Save cleaned data to output directory"""
        # Create output directory if it doesn't exist
        output_path = self.config['data']['output_path']
        os.makedirs(output_path, exist_ok=True)
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(original_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_path, f"{base_name}_cleaned_{timestamp}.csv")
        
        # Save data
        data.to_csv(output_file, index=False)
        self.logger.info(f"Saved cleaned data to: {output_file}")
        
        return output_file
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline configuration status"""
        return {
            'pipeline_name': self.config['pipeline']['name'],
            'version': self.config['pipeline']['version'],
            'agents': {
                name: {
                    'enabled': agent_config['enabled'],
                    'name': agent_config['name']
                }
                for name, agent_config in self.config['agents'].items()
            },
            'data_paths': self.config['data']
        }
    
    def run_batch_pipeline(self, input_directory: str) -> List[PipelineResult]:
        """Run pipeline on all supported files in a directory"""
        results = []
        supported_extensions = ['.csv', '.xlsx', '.xls', '.json', '.parquet']
        
        for filename in os.listdir(input_directory):
            file_path = os.path.join(input_directory, filename)
            file_extension = os.path.splitext(filename)[1].lower()
            
            if os.path.isfile(file_path) and file_extension in supported_extensions:
                self.logger.info(f"Processing file: {filename}")
                result = self.run_pipeline(file_path)
                results.append(result)
        
        return results
