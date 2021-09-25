
 
srv = Riddl::Client.new("https://cpee.org/flow/engine/56932/")
 
### creating new instance
status, response = srv.resource("/").post [
  Riddl::Parameter::Simple.new("name","Monitor Test")
]
ins = response.first.value
 
### if instance not empty monitor it
unless ins.empty?
  puts "Monitoring Instance #{ins}"
  status, response = srv.resource("/#{ins}/notifications/subscriptions/").post [
    Riddl::Parameter::Simple.new("topic","properties/description"),
    Riddl::Parameter::Simple.new("events","change"),
    Riddl::Parameter::Simple.new("topic","properties/state"),
    Riddl::Parameter::Simple.new("events","change"),
  ]
  key = response.first.value
 
  res = srv.resource("/#{ins}/notifications/subscriptions/#{key}/ws/").ws do |conn|
    conn.stream do |msg|
      puts msg
      puts '--------------'
    end
  end
end