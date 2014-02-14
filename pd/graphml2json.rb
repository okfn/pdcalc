#!/usr/bin/ruby

require 'zlib'
require 'stringio'
require "rexml/document"
require 'json'

class Node
  attr_accessor :name
  attr_accessor :text
  attr_accessor :question
  attr_accessor :options

  def initialize(xml)
    # The name (the ID) of the xml
    @name = xml.attributes['id']

    # list of options
    @options = []

    @question = false

    # Getting the configuration type (decision/answer)
    xml.elements.each('data') do |data|
      data.elements.each do |confNode|
        if confNode.name == 'ShapeNode' 
	# and confNode.namespace == 'http://www.yworks.com/xml/graphml'
          @question = true #if confNode.attributes['configuration'] == 'com.yworks.flowchart.decision'

          # Getting the text
          confNode.elements.each do |labelNode|
            if labelNode.name == 'NodeLabel' and
               labelNode.namespace == 'http://www.yworks.com/xml/graphml'
	      #print ">>>>>>  "
	      #print labelNode.text
	      #print "\n"
              @text = make_beauty labelNode.text
            end
          end
        end
      end
    end
  end

  def add_option(node, xml)
    # Getting the text
    xml.elements.each('data') do |data|
      data.elements.each do |polyLineEdge|
        if polyLineEdge.name == 'PolyLineEdge' and
           polyLineEdge.namespace == 'http://www.yworks.com/xml/graphml'
          polyLineEdge.elements.each do |labelEdge|
            if labelEdge.name == 'EdgeLabel' and
               labelEdge.namespace == 'http://www.yworks.com/xml/graphml'
              @options.push( { :text => make_beauty(labelEdge.text),
                               :node => node })
            end
          end
        end
      end
    end
  end

  def valid?
    return false if @name.nil?
    return false if @text.nil?

    true
  end

  def is_question?
    @question
  end

private
  def make_beauty(str)
    str.gsub(/\n/, ' ').strip
  end
end

# the main class
class Graphml2Rdf

  # Initialization with input/output file
  def initialize(input, output)
    @input = input
    @output = output

    @nodes = {}
    @edges = []

    @first_node = nil

    @options_count = 0
  end

  # int main() { ...
  def run
      xml = File.read ARGV[0]

      # gunzipping
      if ARGV[0].end_with?('z')
        gz = Zlib::GzipReader.new(StringIO.new(xml))
        xml = gz.read
         print(xml)
      end

    begin
      doc = REXML::Document.new(xml)
    rescue
    end

    if doc.nil? or
       doc.root.nil? or
       doc.root.name != 'graphml' or
       doc.root.namespace != 'http://graphml.graphdrawing.org/xmlns'
      puts "The input file is not a graphml document."
      return
    end


    # For each node
    doc.elements.each('//node') { |element| manage_node element }

    
    # For each edget
    doc.elements.each('//edge') { |element| manage_edge element }


    preparing = {}
    preparing[:root] = @first_node.name if not @first_node.nil?
    preparing[:questions] = {}

    # For each node:
    #@nodes.each do |name, node|
    #  if node.is_question?
    #    preparing[:questions][name.to_s] = {:type => "question"}
    #  else
    #    preparing[:questions][name.to_s] = {:type => "answer"}
    #  end
    #  
    #  preparing[:questions][name.to_s][:text] => node.text
#
#    #  if node.is_question? and not node.options.empty?
#    #    preparing[:questions][name.to_s][:options] = []
#    #    node.options.each do |option|
#    #      preparing[:questions][name.to_s][:options].push({:text => option[:text], :next => option[:node].name})
#    #    end
#    #  end
    #end

    # Serializing
    File.open(@output, 'w') do |file|
      file.write("{\n")

      file.write("  \"root\":\"" + @first_node.name + "\",\n") if not @first_node.nil?
      file.write("  \"questions\":{")

      oindex = 0
      # For each node:
      @nodes.each do |name, node|
        if node.is_question?
          file.write("    \"" + name.to_s + "\":{\n")
          file.write("      \"type\":\"question\",\n")

        else
          file.write("    \"" + name.to_s + "\":{\n")
          file.write("      \"type\":\"answer\",\n")
        end

        file.write("      \"text\":\"" + node.text + "\"")

        # list of options:
        if node.is_question? and not node.options.empty?
          file.write(",\n")
          file.write("    \"options\":[\n")

          node.options.each_with_index do |option, index|
            file.write("            {\"text\":\"" + option[:text] + "\",\n")
            file.write("            \"node\":\"" + option[:node].name + "\"}")
            if index < node.options.size - 1
              file.write(",");
            end
            file.write("\n");
          end

          file.write("     ]\n");
        end

        file.write("   }");
        if oindex < @nodes.size - 1
          file.write(",");
        end
        file.write("\n");
        oindex += 1 
      end

      file.write("  }\n");
      file.write("}\n");
    end
  end

private
  def manage_node(node)
    new_node = Node.new(node)
    if new_node.valid?
      @first_node = new_node if @first_node.nil?
      @nodes[new_node.name] = new_node
    end
  end

  def manage_edge(node)
    source = nil
    if not node.attributes['source'].nil?
       @nodes.include?(node.attributes['source'])
      source = @nodes[node.attributes['source']]
    end

    target = nil
    if not node.attributes['target'].nil?
       @nodes.include?(node.attributes['target'])
      target = @nodes[node.attributes['target']]
    end

    if not source.nil? and not target.nil?
      source.add_option(target, node)
    end
  end
end

def usage
  puts "Usage: graphml2rdf <input> <output>"
end

if ARGV.size != 2 or not File.exists?(ARGV[0])
  usage
end

app = Graphml2Rdf.new(ARGV[0], ARGV[1])
app.run

