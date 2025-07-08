import pytest
from unittest.mock import MagicMock
from src.llm_processor import LLMProcessor

@pytest.fixture
def mock_chat_openai(monkeypatch):
    """Fixture to mock ChatOpenAI class."""
    mock = MagicMock()
    mock.model = "gpt-3.5-turbo"
    monkeypatch.setattr("langchain_openai.ChatOpenAI", MagicMock(return_value=mock))
    return mock

def test_llm_processor_init(mock_chat_openai):
    """Test LLMProcessor initialization."""
    llm_processor = LLMProcessor(api_key="test_key")
    assert llm_processor.llm.model == "gpt-3.5-turbo"
    mock_chat_openai.assert_called_once_with(model="gpt-3.5-turbo", api_key="test_key")

def test_suggest_column_names(mock_chat_openai):
    """Test suggest_column_names method with mocked LLM response."""
    llm_processor = LLMProcessor(api_key="test_key")
    mock_response = '{"col1": "column_one", "col2": "column_two"}'
    llm_processor.llm.run = MagicMock(return_value=mock_response)
    
    df = MagicMock()  # Mock pandas DataFrame
    df.columns = ["col1", "col2"]
    df.head.return_value.to_dict.return_value = {"col1": [1, 2], "col2": ["a", "b"]}
    
    result = llm_processor.suggest_column_names(df)
    assert result == {"col1": "column_one", "col2": "column_two"}
    llm_processor.llm.run.assert_called_once()