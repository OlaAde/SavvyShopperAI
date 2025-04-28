from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.llms import Ollama
from pydantic import BaseModel, Field
from typing import Optional


class CarSearch(BaseModel):
    car_name_model: str = Field(description="Only the car make and model (e.g., 'Honda Civic', 'Toyota Camry')")
    transmission: Optional[str] = Field(description="Transmission type: 'Automatic', 'Manual', or None if not specified")
    min_year: Optional[str] = Field(description="Minimum year of the car, or None if not specified")
    max_year: Optional[str] = Field(description="Maximum year of the car, or None if not specified")

def extract_structured_query(query):
    parser = JsonOutputParser(pydantic_object=CarSearch)

    prompt = ChatPromptTemplate.from_template(
        """
        Extract the car search information from the following prompt into separate fields:

        User input: {user_input}

        IMPORTANT INSTRUCTIONS:
        1. For car_name_model: Extract ONLY the car make and model (e.g., "Honda Civic", "Toyota Camry")
           - Do NOT include transmission type or years in this field
           - Only include the manufacturer and model name

        2. For transmission: Extract ONLY "Automatic", "Manual", or "Manual" if not specified

        3. For min_year: Extract ONLY the minimum year or "None" if not specified

        4. For max_year: Extract ONLY the maximum year or "None" if not specified

        If a parameter is not provided in the user input, output "None" for that field.

        {format_instructions}
        """
    )

    format_instructions = parser.get_format_instructions()
    prompt = prompt.partial(format_instructions=format_instructions)

    llm = Ollama(model="llama3")

    chain = prompt | llm | parser

    return chain.invoke({"user_input": query})