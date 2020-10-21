from flask import Flask, render_template, flash, request
import openai
import uuid
openai.api_key = "sk-s4frvyLkeErBmZOVPdQN4n6dBZoCVV6wFvT6bLky"
response = openai.Completion.create(engine="davinci", prompt="This is a test", max_tokens=5)

class Example:
    """Stores an input, output pair and formats it to prime the model."""
    def __init__(self, inp, out):
        self.input = inp
        self.output = out
        self.id = uuid.uuid4().hex
    
    def get_id(self):
        """Returns the unique ID of the example."""
        return self.id
    
    def get_input(self):
        """Returns the input of the example."""
        return self.input

    def get_output(self):
        """Returns the intended output of the example."""
        return self.output

    def get_id(self):
        """Returns the unique ID of the example."""
        return self.id

    def as_dict(self):
        return {
            "input": self.get_input(),
            "output": self.get_output(),
            "id": self.get_id(),
        }


class GPT:
    """The main class for a user to interface with the OpenAI API.
    A user can add examples and set parameters of the API request.
    """
    def __init__(self,
                 engine='davinci',
                 temperature=0.5,
                 max_tokens=100,
                 input_prefix="input: ",
                 input_suffix="\n",
                 output_prefix="output: ",
                 output_suffix="\n\n",
                 append_output_prefix_to_query=False):
        self.examples = {}
        self.engine = engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.input_prefix = input_prefix
        self.input_suffix = input_suffix
        self.output_prefix = output_prefix
        self.output_suffix = output_suffix
        self.append_output_prefix_to_query = append_output_prefix_to_query
        self.stop = (output_suffix + input_prefix).strip()
    
    def get_engine(self):
        """Returns the engine specified for the API."""
        return self.engine

    def get_temperature(self):
        """Returns the temperature specified for the API."""
        return self.temperature

    def get_max_tokens(self):
        """Returns the max tokens specified for the API."""
        return self.max_tokens
    
    def get_prime_text(self):
        """Formats all examples to prime the model."""
        return "".join(
            [self.format_example(ex) for ex in self.examples.values()])
    
    def craft_query(self, prompt):
        """Creates the query for the API request."""
        q = self.get_prime_text(
        ) + self.input_prefix + prompt + self.input_suffix
        if self.append_output_prefix_to_query:
            q = q + self.output_prefix

        return q

    def add_example(self, ex):
        """Adds an example to the object.
        Example must be an instance of the Example class.
        """
        assert isinstance(ex, Example), "Please create an Example object."
        self.examples[ex.get_id()] = ex

    def submit_request(self, prompt):
        """Calls the OpenAI API with the specified parameters."""
        response = openai.Completion.create(engine=self.get_engine(),
                                            prompt=self.craft_query(prompt),
                                            max_tokens=self.get_max_tokens(),
                                            temperature=self.get_temperature(),
                                            top_p=1,
                                            n=1,
                                            stream=False,
                                            stop=self.stop)
        return response
    
    def get_top_reply(self, prompt):
        """Obtains the best result as returned by the API."""
        response = self.submit_request(prompt)
        return response['choices'][0]['text']

    def format_example(self, ex):
        """Formats the input, output pair."""
        return self.input_prefix + ex.get_input(
        ) + self.input_suffix + self.output_prefix + ex.get_output(
        ) + self.output_suffix


sentences = [ [r'Subject to the approval of the Company’s Board of Directors (the “Board”), the Company shall grant you a stock option covering 10,000 shares of the Company’s Common Stock (the “Option”).',
              r'The company is granting 10,000 shares of stock.'], 
              [r'The Option shall be granted as soon as reasonably practicable after the date of this Agreement or, if later, the date you commence full-time Employment.',
              r'The option is granted as soon as you begin employment.'], 
              [r'The exercise price per share will be equal to the fair market value per share on the date the Option is granted, as determined by the Board in good faith compliance with applicable guidance in order to avoid having the Option be treated as deferred compensation under Section 409A of the Internal Revenue Code of 1986, as amended. There is no guarantee that the Internal Revenue Service will agree with this value.',
              r'The value of shares will be determined by the company’s most recent priced valuation (409A), there is no guarantee to their final value.'], 
              [r'You should consult with your own tax advisor concerning the tax risks associated with accepting an option to purchase the Company’s Common Stock.',
              r'Consult with a tax advisor regarding tax risks in regards to options purchase.'],
              [r'The term of the Option shall be ten (10) years, subject to earlier expiration in the event of the termination of your services to the Company. The Option shall vest and become exercisable at the rate of 25% of the total number of option shares after the first twelve (12) months of continuous service and the remaining option shares shall become vested and exercisable in equal monthly installments over the next three (3) years of continuous service.',
              r'You have 10 years to exercise options and the vesting schedule is as follows: 25% vests after 12 months and the remaining vests via equal monthly installments over 3 years.'],
              [r'The Option will be an incentive stock option to the maximum extent allowed by the tax code and shall be subject to the other terms and conditions set forth in the Company’s 2015 Stock Plan and in the Companys standard form of Stock Option Agreement.',
              r'The options type is an incentive stock option, check the company’s 2015 stock plan and in the company’s standard form of stock option agreement. ']
            ]

# create models
model = GPT(engine = "davinci", temperature = 0.5, max_tokens = 100)
for sentence in sentences:
    model.add_example(Example(sentence[0], sentence[1]))


def translate(text):
    return model.submit_request(text).choices[0].text[8:]

app = Flask(__name__)

@app.route('/')
@app.route('/', methods = ['GET'])
def index():
  return render_template('index.html')

@app.route('/', methods = ['POST'])
def results():
  offer = request.form['offer']
  offer = translate(offer)
  return render_template('results.html', translation = offer)


if __name__ == '__main__':
  app.run(debug=True)