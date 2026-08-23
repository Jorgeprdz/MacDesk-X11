-- Extract the first X.509 certificate from an APK Signature Scheme v2/v3 block.
-- Usage: lua extract-apk-signing-cert.lua input.apk output.der
local input, output = arg[1], arg[2]
assert(input and output, "usage: extract-apk-signing-cert.lua input.apk output.der")

local f = assert(io.open(input, "rb"))
local data = assert(f:read("*a"))
f:close()

local magic = "APK Sig Block 42"
local magic_pos, search = nil, 1
while true do
  local p = data:find(magic, search, true)
  if not p then break end
  magic_pos, search = p, p + 1
end
assert(magic_pos, "APK signing block not found")

local function u32(pos)
  local value
  value, pos = string.unpack("<I4", data, pos)
  return value, pos
end

local function u64(pos)
  local value
  value, pos = string.unpack("<I8", data, pos)
  return value, pos
end

local footer_size = u64(magic_pos - 8)
local block_start = magic_pos + 8 - footer_size
local header_size = u64(block_start)
assert(header_size == footer_size, "APK signing block size mismatch")

local pair_pos = block_start + 8
local pairs_end = magic_pos - 8
local wanted = { [0x7109871a] = true, [0xf05368c0] = true }
local value_pos, value_len
while pair_pos < pairs_end do
  local pair_len, after_len = u64(pair_pos)
  local id, after_id = u32(after_len)
  if wanted[id] then
    value_pos, value_len = after_id, pair_len - 4
    break
  end
  pair_pos = after_len + pair_len
end
assert(value_pos and value_len, "APK v2/v3 signer block not found")

-- value -> length-prefixed signers -> first signer -> signed data
local _, signers_pos = u32(value_pos)
local _, signer_pos = u32(signers_pos)
local _, signed_data_pos = u32(signer_pos)

-- signed data -> digests -> certificates -> first certificate
local digests_len, after_digests_len = u32(signed_data_pos)
local certs_len_pos = after_digests_len + digests_len
local certs_len, certs_pos = u32(certs_len_pos)
assert(certs_len > 4, "empty certificate sequence")
local cert_len, cert_pos = u32(certs_pos)
assert(cert_len > 0 and cert_len <= certs_len - 4, "invalid certificate length")

local cert = data:sub(cert_pos, cert_pos + cert_len - 1)
local out = assert(io.open(output, "wb"))
assert(out:write(cert))
out:close()
